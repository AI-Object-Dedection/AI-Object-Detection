"""empty message

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'MANAGER', 'VIEWER', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'ARCHIVED', 'COMPLETED', name='projectstatus'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    
    # Create project_members table
    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'EDITOR', 'VIEWER', name='projectmemberrole'), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_members_id'), 'project_members', ['id'], unique=False)
    
    # Create images table
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('uploader_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('thumbnail_path', sa.String(), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('taken_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ai_status', sa.Enum('PENDING', 'PROCESSING', 'DONE', 'FAILED', name='aistatus'), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'DONE', 'FAILED', name='imagestatus'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_id'), 'images', ['id'], unique=False)
    
    # Create image_descriptions table
    op.create_table(
        'image_descriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('description_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('ppe_detected', sa.String(), nullable=True),
        sa.Column('safety_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_descriptions_id'), 'image_descriptions', ['id'], unique=False)
    op.create_index(op.f('ix_image_descriptions_image_id'), 'image_descriptions', ['image_id'], unique=True)
    
    # Create image_embeddings table with vector column
    op.create_table(
        'image_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('embedding_model', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_embeddings_id'), 'image_embeddings', ['id'], unique=False)
    op.create_index(op.f('ix_image_embeddings_image_id'), 'image_embeddings', ['image_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_image_embeddings_image_id'), table_name='image_embeddings')
    op.drop_index(op.f('ix_image_embeddings_id'), table_name='image_embeddings')
    op.drop_table('image_embeddings')
    
    op.drop_index(op.f('ix_image_descriptions_image_id'), table_name='image_descriptions')
    op.drop_index(op.f('ix_image_descriptions_id'), table_name='image_descriptions')
    op.drop_table('image_descriptions')
    
    op.drop_index(op.f('ix_images_id'), table_name='images')
    op.drop_table('images')
    
    op.drop_index(op.f('ix_project_members_id'), table_name='project_members')
    op.drop_table('project_members')
    
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS aistatus')
    op.execute('DROP TYPE IF EXISTS imagestatus')
    op.execute('DROP TYPE IF EXISTS projectmemberrole')
    op.execute('DROP TYPE IF EXISTS projectstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
