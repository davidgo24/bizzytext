from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f74ad2634ad'
down_revision = None  # 👈 or set to the previous revision's ID if there is one
branch_labels = None
depends_on = None


def upgrade():
    # ✅ Add owner_id column to appointment table
    op.add_column('appointment', sa.Column('owner_id', sa.Integer(), nullable=True))
    
    # ✅ Optionally add foreign key (skip if not needed right now)
    op.create_foreign_key(
        'fk_appointment_owner_id',      # name of the constraint
        'appointment',                  # source table
        'owner',                        # target table
        ['owner_id'],                   # source column(s)
        ['id']                          # target column(s)
    )


def downgrade():
    # 🔁 Rollback logic
    op.drop_constraint('fk_appointment_owner_id', 'appointment', type_='foreignkey')
    op.drop_column('appointment', 'owner_id')
