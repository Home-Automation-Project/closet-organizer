"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# create_type=False on postgresql.ENUM prevents op.create_table from auto-creating enums.
# We create them explicitly via op.execute() with IF NOT EXISTS instead.
basket_type = ENUM(
    "BEDDING", "CLEANING", "FIRST_AID_BASIC", "FIRST_AID_ADVANCED",
    name="baskettype", create_type=False,
)
shelf_event_type = ENUM("OCCUPIED", "EMPTY", name="shelfeventtype", create_type=False)
item_frequency = ENUM("DAILY", "WEEKLY", "MONTHLY", "SEASONAL", name="itemfrequency", create_type=False)
reminder_category = ENUM("CLEANING", "FIRST_AID", "BEDDING", name="remindercategory", create_type=False)


def upgrade() -> None:
    # Create enums via PL/pgSQL DO blocks (safe for re-runs)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE baskettype AS ENUM ('BEDDING', 'CLEANING', 'FIRST_AID_BASIC', 'FIRST_AID_ADVANCED');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE shelfeventtype AS ENUM ('OCCUPIED', 'EMPTY');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE itemfrequency AS ENUM ('DAILY', 'WEEKLY', 'MONTHLY', 'SEASONAL');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE remindercategory AS ENUM ('CLEANING', 'FIRST_AID', 'BEDDING');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # Closets
    op.create_table(
        "closets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("location", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Shelves
    op.create_table(
        "shelves",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("closet_id", sa.Integer, sa.ForeignKey("closets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(120)),
        sa.Column("position_order", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Baskets
    op.create_table(
        "baskets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("shelf_id", sa.Integer, sa.ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("basket_type", basket_type, nullable=False),
        sa.Column("sub_bin", sa.String(60)),
        sa.Column("nfc_tag_id", sa.String(200), unique=True),
        sa.Column("qr_token", sa.String(36), unique=True, nullable=False),
        sa.Column("position_order", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Item Definitions
    op.create_table(
        "item_definitions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("basket_type", basket_type, nullable=False),
        sa.Column("sub_bin", sa.String(60)),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(120)),
        sa.Column("has_expiration", sa.Boolean, default=False),
        sa.Column("recommended_qty", sa.Integer, default=1),
        sa.Column("unit", sa.String(60)),
    )

    # Basket Inventory
    op.create_table(
        "basket_inventory",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("basket_id", sa.Integer, sa.ForeignKey("baskets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_definition_id", sa.Integer, sa.ForeignKey("item_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer, default=0),
        sa.Column("expiration_date", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Shelf Events
    op.create_table(
        "shelf_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("shelf_id", sa.Integer, sa.ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", shelf_event_type, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Wash Reminders
    op.create_table(
        "wash_reminders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("shelf_id", sa.Integer, sa.ForeignKey("shelves.id", ondelete="CASCADE"), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
    )

    # Cleaning Logs
    op.create_table(
        "cleaning_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("basket_id", sa.Integer, sa.ForeignKey("baskets.id", ondelete="SET NULL")),
        sa.Column("room_type", sa.String(80), nullable=False),
        sa.Column("cleaned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("checklist_snapshot", sa.JSON),
    )

    # Seasonal Reminders
    op.create_table(
        "seasonal_reminders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("basket_id", sa.Integer, sa.ForeignKey("baskets.id", ondelete="SET NULL")),
        sa.Column("category", reminder_category, nullable=False),
        sa.Column("reminder_text", sa.String(500), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Checklist Items
    op.create_table(
        "checklist_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_type", sa.String(80), nullable=False),
        sa.Column("category", sa.String(120)),
        sa.Column("item_key", sa.String(200), nullable=False),
        sa.Column("description", sa.String(400), nullable=False),
        sa.Column("frequency", item_frequency, nullable=False),
        sa.Column("sort_order", sa.Integer, default=0),
    )

    # Checklist Completions
    op.create_table(
        "checklist_completions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_type", sa.String(80), nullable=False),
        sa.Column("item_key", sa.String(200), nullable=False),
        sa.Column("session_token", sa.String(36), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Family Members
    op.create_table(
        "family_members",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("date_of_birth", sa.String(20)),
        sa.Column("blood_type", sa.String(10)),
        sa.Column("allergies", sa.Text),
        sa.Column("medications", sa.Text),
        sa.Column("medical_conditions", sa.Text),
        sa.Column("emergency_contact", sa.String(200)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("family_members")
    op.drop_table("checklist_completions")
    op.drop_table("checklist_items")
    op.drop_table("seasonal_reminders")
    op.drop_table("cleaning_logs")
    op.drop_table("wash_reminders")
    op.drop_table("shelf_events")
    op.drop_table("basket_inventory")
    op.drop_table("item_definitions")
    op.drop_table("baskets")
    op.drop_table("shelves")
    op.drop_table("closets")

    reminder_category.drop(op.get_bind(), checkfirst=True)
    item_frequency.drop(op.get_bind(), checkfirst=True)
    shelf_event_type.drop(op.get_bind(), checkfirst=True)
    basket_type.drop(op.get_bind(), checkfirst=True)
