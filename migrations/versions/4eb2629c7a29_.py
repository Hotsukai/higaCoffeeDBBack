"""empty message

Revision ID: 4eb2629c7a29
Revises: a8a00cd5afc9
Create Date: 2020-12-22 13:40:55.532408

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4eb2629c7a29'
down_revision = 'a8a00cd5afc9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coffees', 'powder_amount',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)
    op.alter_column('coffees', 'water_amount',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Integer(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coffees', 'water_amount',
               existing_type=sa.Integer(),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.alter_column('coffees', 'powder_amount',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
