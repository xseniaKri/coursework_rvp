import io
from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.category import Category
from app.models.enums import EventStatus, Role
from app.models.event import Event
from app.models.structure_unit import StructureUnit
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(get_current_user)])

MONTH_NAMES_RU = [
    "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
]


def _xlsx_response(buf: io.BytesIO, filename: str) -> StreamingResponse:
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _last_month() -> tuple[int, int]:
    today = date.today()
    if today.month == 1:
        return 12, today.year
    return today.month, today.year


def _mode_or_dash(series: pd.Series) -> str:
    if series.empty:
        return "-"
    counts = series.value_counts()
    if len(counts) == 1 or counts.iloc[0] > counts.iloc[1]:
        return str(counts.index[0])
    return "-"


def _fmt_pct(val: float | None) -> str:
    if val is None or pd.isna(val):
        return "—"
    return f"{val:.1f}%"


@router.get("/monthly")
async def monthly_report(
    session: AsyncSession = Depends(get_db),
):
    month, year = _last_month()

    result = await session.execute(
        select(
            Event.title,
            Event.status,
            Category.name.label("category"),
        )
        .join(Category, Event.category_id == Category.id)
        .where(
            extract("year", Event.planned_date) == year,
            extract("month", Event.planned_date) == month,
        )
    )
    rows = result.mappings().all()

    df = pd.DataFrame([
        {"title": r["title"], "status": str(r["status"]), "category": r["category"]}
        for r in rows
    ])

    completed_str = str(EventStatus.COMPLETED)
    planned_str = str(EventStatus.PLANNED)

    completed_count = int((df["status"] == completed_str).sum()) if not df.empty else 0
    planned_count = int((df["status"] == planned_str).sum()) if not df.empty else 0

    completed_df = df[df["status"] == completed_str] if not df.empty else pd.DataFrame(columns=["title", "status", "category"])
    by_cat = (
        completed_df.groupby("category").size()
        .reset_index(name="Проведено")
        .rename(columns={"category": "Категория"})
        if not completed_df.empty
        else pd.DataFrame({"Категория": [], "Проведено": []})
    )

    top_category = _mode_or_dash(completed_df["category"]) if not completed_df.empty else "-"

    month_label = MONTH_NAMES_RU[month]
    summary_df = pd.DataFrame({
        "Показатель": ["Проведено мероприятий", "Запланировано мероприятий", "Самая частая категория"],
        "Значение": [completed_count, planned_count, top_category],
    })

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name=f"Итог ({month_label} {year})", index=False)
        by_cat.to_excel(writer, sheet_name="По категориям", index=False)

    return _xlsx_response(buf, f"monthly_{month:02d}_{year}.xlsx")


@router.get("/employees")
async def employees_report(
    session: AsyncSession = Depends(get_db),
):
    ev_result = await session.execute(
        select(
            Event.status,
            Event.author_id,
            Event.responsible_id,
            Category.name.label("category"),
        ).join(Category, Event.category_id == Category.id)
    )
    u_result = await session.execute(
        select(User.id, User.full_name).where(User.role != Role.ADMIN)
    )

    ev_rows = ev_result.mappings().all()
    user_rows = u_result.mappings().all()

    df_events = pd.DataFrame([
        {
            "status": str(r["status"]),
            "author_id": r["author_id"],
            "responsible_id": r["responsible_id"],
            "category": r["category"],
        }
        for r in ev_rows
    ]) if ev_rows else pd.DataFrame(columns=["status", "author_id", "responsible_id", "category"])

    df_users = pd.DataFrame([{"id": r["id"], "Сотрудник": r["full_name"]} for r in user_rows])

    completed_str = str(EventStatus.COMPLETED)
    rejected_str = str(EventStatus.REJECTED)
    planned_str = str(EventStatus.PLANNED)

    df_completed = df_events[df_events["status"] == completed_str] if not df_events.empty else df_events.copy()

    created = (
        df_events.groupby("author_id").size()
        .reset_index(name="Создано мероприятий")
        .rename(columns={"author_id": "id"})
        if not df_events.empty
        else pd.DataFrame(columns=["id", "Создано мероприятий"])
    )

    conducted = (
        df_completed.dropna(subset=["responsible_id"])
        .groupby("responsible_id").size()
        .reset_index(name="Проведено мероприятий")
        .rename(columns={"responsible_id": "id"})
        if not df_completed.empty
        else pd.DataFrame(columns=["id", "Проведено мероприятий"])
    )
    if not conducted.empty:
        conducted["id"] = conducted["id"].astype(int)

    if not df_events.empty:
        total_by_author = (
            df_events.groupby("author_id").size()
            .reset_index(name="total")
            .rename(columns={"author_id": "id"})
        )
        rejected_by_author = (
            df_events[df_events["status"] == rejected_str]
            .groupby("author_id").size()
            .reset_index(name="rejected")
            .rename(columns={"author_id": "id"})
        )
        rej = total_by_author.merge(rejected_by_author, on="id", how="left").fillna(0)
        rej["% отклоненных"] = (rej["rejected"] / rej["total"] * 100).round(1)
        rejection_rate = rej[["id", "% отклоненных"]]
    else:
        rejection_rate = pd.DataFrame(columns=["id", "% отклоненных"])

    if not df_events.empty and df_events["responsible_id"].notna().any():
        df_resp = df_events.dropna(subset=["responsible_id"]).copy()
        df_resp["responsible_id"] = df_resp["responsible_id"].astype(int)
        df_resp_pc = df_resp[df_resp["status"].isin([planned_str, completed_str])]
        total_pc = (
            df_resp_pc.groupby("responsible_id").size()
            .reset_index(name="total_pc")
            .rename(columns={"responsible_id": "id"})
        )
        count_planned_resp = (
            df_resp[df_resp["status"] == planned_str]
            .groupby("responsible_id").size()
            .reset_index(name="planned_count")
            .rename(columns={"responsible_id": "id"})
        )
        pl = total_pc.merge(count_planned_resp, on="id", how="left").fillna(0)
        pl["% незавершённых"] = (pl["planned_count"] / pl["total_pc"] * 100).round(1)
        planned_rate = pl[["id", "% незавершённых"]]
    else:
        planned_rate = pd.DataFrame(columns=["id", "% незавершённых"])

    summary = df_users.copy()
    summary = summary.merge(created, on="id", how="left")
    summary = summary.merge(conducted, on="id", how="left")
    summary["Создано мероприятий"] = summary["Создано мероприятий"].fillna(0).astype(int)
    summary["Проведено мероприятий"] = summary["Проведено мероприятий"].fillna(0).astype(int)
    summary = summary.merge(rejection_rate, on="id", how="left")
    summary = summary.merge(planned_rate, on="id", how="left")
    summary["% отклоненных"] = summary["% отклоненных"].apply(_fmt_pct)
    summary["% незавершённых"] = summary["% незавершённых"].apply(_fmt_pct)

    if not df_completed.empty and df_completed["responsible_id"].notna().any():
        cat_df = df_completed.dropna(subset=["responsible_id"]).copy()
        cat_df["responsible_id"] = cat_df["responsible_id"].astype(int)
        pivot = (
            cat_df.pivot_table(index="responsible_id", columns="category", aggfunc="size", fill_value=0)
            .reset_index()
            .rename(columns={"responsible_id": "id"})
        )
        pivot.columns.name = None
        by_cat = df_users.merge(pivot, on="id", how="left").fillna(0)
        for col in by_cat.columns:
            if col not in ("id", "Сотрудник"):
                by_cat[col] = by_cat[col].astype(int)
    else:
        by_cat = df_users.copy()

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        summary.drop(columns=["id"]).to_excel(writer, sheet_name="Сотрудники", index=False)
        by_cat.drop(columns=["id"]).to_excel(writer, sheet_name="По категориям", index=False)

    return _xlsx_response(buf, "employees_report.xlsx")


@router.get("/structure-units")
async def structure_units_report(
    session: AsyncSession = Depends(get_db),
):
    su_result = await session.execute(select(StructureUnit.id, StructureUnit.name))
    u_result = await session.execute(
        select(User.id, User.su_id).where(User.role != Role.ADMIN)
    )
    ev_result = await session.execute(
        select(
            Event.id,
            Category.name.label("category"),
            User.su_id.label("resp_su_id"),
        )
        .join(Category, Event.category_id == Category.id)
        .outerjoin(User, Event.responsible_id == User.id)
        .where(Event.status == EventStatus.COMPLETED)
    )

    su_rows = su_result.mappings().all()
    user_rows = u_result.mappings().all()
    ev_rows = ev_result.mappings().all()

    df_su = pd.DataFrame([{"su_id": r["id"], "СП": r["name"]} for r in su_rows])
    df_users = pd.DataFrame([{"id": r["id"], "su_id": r["su_id"]} for r in user_rows]) if user_rows else pd.DataFrame(columns=["id", "su_id"])
    df_completed = pd.DataFrame([
        {"category": r["category"], "resp_su_id": r["resp_su_id"]}
        for r in ev_rows
    ]) if ev_rows else pd.DataFrame(columns=["category", "resp_su_id"])

    emp_count = (
        df_users.groupby("su_id").size()
        .reset_index(name="Кол-во сотрудников")
        if not df_users.empty
        else pd.DataFrame(columns=["su_id", "Кол-во сотрудников"])
    )

    conducted = (
        df_completed.dropna(subset=["resp_su_id"])
        .groupby("resp_su_id").size()
        .reset_index(name="Проведено мероприятий")
        .rename(columns={"resp_su_id": "su_id"})
        if not df_completed.empty
        else pd.DataFrame(columns=["su_id", "Проведено мероприятий"])
    )
    if not conducted.empty:
        conducted["su_id"] = conducted["su_id"].astype(int)

    summary = (
        df_su
        .merge(emp_count, on="su_id", how="left")
        .merge(conducted, on="su_id", how="left")
        .fillna(0)
    )
    summary["Кол-во сотрудников"] = summary["Кол-во сотрудников"].astype(int)
    summary["Проведено мероприятий"] = summary["Проведено мероприятий"].astype(int)

    if not df_completed.empty and df_completed["resp_su_id"].notna().any():
        cat_df = df_completed.dropna(subset=["resp_su_id"]).copy()
        cat_df["resp_su_id"] = cat_df["resp_su_id"].astype(int)
        pivot = (
            cat_df.pivot_table(index="resp_su_id", columns="category", aggfunc="size", fill_value=0)
            .reset_index()
            .rename(columns={"resp_su_id": "su_id"})
        )
        pivot.columns.name = None
        by_cat = df_su.merge(pivot, on="su_id", how="left").fillna(0)
        for col in by_cat.columns:
            if col not in ("su_id", "СП"):
                by_cat[col] = by_cat[col].astype(int)
    else:
        by_cat = df_su.copy()

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        summary.drop(columns=["su_id"]).to_excel(writer, sheet_name="По СП", index=False)
        by_cat.drop(columns=["su_id"]).to_excel(writer, sheet_name="По категориям", index=False)

    return _xlsx_response(buf, "structure_units_report.xlsx")
