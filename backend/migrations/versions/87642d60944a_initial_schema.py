"""initial schema

Revision ID: 87642d60944a
Revises:
Create Date: 2026-02-28 06:02:38.319739

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '87642d60944a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('card_type', sa.String(), nullable=False),
        sa.Column('source_set', sa.String(), nullable=False),
        sa.Column('aspect', sa.String(), nullable=True),
        sa.Column('cost', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('is_expert', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'storylines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('min_rangers', sa.Integer(), nullable=False),
        sa.Column('max_rangers', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('storyline_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['storyline_id'], ['storylines.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'storyline_day_presets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('storyline_id', sa.Integer(), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('weather', sa.String(), nullable=False),
        sa.Column('default_location', sa.String(), nullable=True),
        sa.Column('default_path_terrain', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['storyline_id'], ['storylines.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'campaign_collaborators',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('campaign_id', 'user_id'),
    )
    op.create_table(
        'campaign_days',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('weather', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('path_terrain', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'campaign_rewards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('card_name', sa.String(), nullable=True),
        sa.Column('card_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'rangers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('aspect_card_name', sa.String(), nullable=False),
        sa.Column('awa', sa.Integer(), nullable=False),
        sa.Column('fit', sa.Integer(), nullable=False),
        sa.Column('foc', sa.Integer(), nullable=False),
        sa.Column('spi', sa.Integer(), nullable=False),
        sa.Column('personality_card_ids', sa.JSON(), nullable=False),
        sa.Column('background_set', sa.String(), nullable=False),
        sa.Column('background_card_ids', sa.JSON(), nullable=False),
        sa.Column('specialty_set', sa.String(), nullable=False),
        sa.Column('specialty_card_ids', sa.JSON(), nullable=False),
        sa.Column('role_card_id', sa.Integer(), nullable=False),
        sa.Column('outside_interest_card_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['role_card_id'], ['cards.id']),
        sa.ForeignKeyConstraint(['outside_interest_card_id'], ['cards.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'missions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('day_started_id', sa.Integer(), nullable=True),
        sa.Column('day_completed_id', sa.Integer(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('max_progress', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['day_started_id'], ['campaign_days.id']),
        sa.ForeignKeyConstraint(['day_completed_id'], ['campaign_days.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'notable_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('day_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['day_id'], ['campaign_days.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'ranger_trades',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ranger_id', sa.Integer(), nullable=False),
        sa.Column('day_id', sa.Integer(), nullable=False),
        sa.Column('original_card_id', sa.Integer(), nullable=False),
        sa.Column('reward_card_id', sa.Integer(), nullable=False),
        sa.Column('reverted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ranger_id'], ['rangers.id']),
        sa.ForeignKeyConstraint(['day_id'], ['campaign_days.id']),
        sa.ForeignKeyConstraint(['original_card_id'], ['cards.id']),
        sa.ForeignKeyConstraint(['reward_card_id'], ['cards.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('ranger_trades')
    op.drop_table('notable_events')
    op.drop_table('missions')
    op.drop_table('rangers')
    op.drop_table('campaign_rewards')
    op.drop_table('campaign_days')
    op.drop_table('campaign_collaborators')
    op.drop_table('storyline_day_presets')
    op.drop_table('campaigns')
    op.drop_table('users')
    op.drop_table('storylines')
    op.drop_table('cards')
