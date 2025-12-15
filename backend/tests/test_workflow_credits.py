"""
Test cases for workflow credit deduction.
Ensures that full_workflow endpoints deduct only 1 credit, not 2.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


class TestWorkflowCreditDeduction:
    """Test cases for workflow credit deduction (verify single credit deduction)."""

    @pytest.mark.asyncio
    async def test_full_workflow_deducts_only_one_credit(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """
        Test that full workflow (with thumbnails) deducts only 1 credit total.
        
        This is a regression test for the bug where:
        - full_workflow deducted 1 credit
        - Then called generate_thumbnails endpoint which deducted another credit
        - Result: 2 credits deducted instead of 1
        
        After fix:
        - full_workflow deducts 1 credit
        - Calls thumbnail service directly (not the endpoint)
        - Result: 1 credit deducted total
        """
        from backend.models.db_models import User
        from sqlalchemy import select

        user_id = authenticated_user["user"]["id"]

        # Give user 10 credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 10
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Mock the script and thumbnail services to avoid actual API calls
        with patch('backend.routers.script.generate_youtube_script') as mock_script:
            with patch('backend.services.thumbnail_service.ThumbnailService.generate_batch_with_storage') as mock_thumb:
                mock_script.return_value = {
                    "script": "Test script content",
                    "success": True,
                    "refined_query": "test query refined",
                    "original_query": "test topic",
                    "videos_analyzed": 5,
                    "stats": {"word_count": 100},
                }
                mock_thumb.return_value = {
                    "success": True,
                    "thumbnails": [
                        {"url": "http://test.com/thumb1.jpg"},
                        {"url": "http://test.com/thumb2.jpg"},
                        {"url": "http://test.com/thumb3.jpg"},
                    ],
                    "successful_count": 3,
                }

                response = await client.post(
                    "/generate/full-workflow",
                    json={
                        "topic": "Test workflow topic",
                        "enable_thumbnails": True,
                        "num_thumbnails": 3,
                        "resolution": "1K",
                    },
                    headers=headers,
                )

        # Refresh user from DB to get updated credit count
        await db_session.refresh(user)

        # CRITICAL: Should have deducted ONLY 1 credit (not 2)
        assert user.credits == 9, f"Expected 9 credits but got {user.credits}. Bug: double credit deduction!"

    @pytest.mark.asyncio
    async def test_full_workflow_without_thumbnails_deducts_one_credit(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that full workflow without thumbnails still deducts 1 credit."""
        from backend.models.db_models import User
        from sqlalchemy import select

        user_id = authenticated_user["user"]["id"]

        # Give user credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 10
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Mock the script service
        with patch('backend.routers.script.generate_youtube_script') as mock_script:
            mock_script.return_value = {
                "script": "Test script",
                "success": True,
                "refined_query": "test query",
                "original_query": "test",
                "videos_analyzed": 5,
            }

            response = await client.post(
                "/generate/full-workflow",
                json={
                    "topic": "Test workflow topic",
                    "enable_thumbnails": False,
                },
                headers=headers,
            )

        # Refresh user from DB
        await db_session.refresh(user)

        # Should have deducted 1 credit
        assert user.credits == 9

    @pytest.mark.asyncio
    async def test_streaming_workflow_deducts_only_one_credit(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that streaming workflow with thumbnails deducts only 1 credit."""
        from backend.models.db_models import User
        from sqlalchemy import select

        user_id = authenticated_user["user"]["id"]

        # Give user credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 10
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Mock the workflow service stream generator
        async def mock_stream(*args, **kwargs):
            yield 'data: {"type": "progress", "step": "initializing"}\n\n'
            yield 'data: {"type": "complete"}\n\n'

        with patch('backend.services.workflow_service.WorkflowStreamService.generate_stream') as mock_gen:
            mock_gen.return_value = mock_stream()

            response = await client.post(
                "/generate/full-workflow/stream",
                json={
                    "topic": "Test streaming workflow",
                    "enable_thumbnails": True,
                    "num_thumbnails": 2,
                },
                headers=headers,
            )

            # Consume the stream
            async for _ in response.aiter_bytes():
                pass

        # Refresh user from DB
        await db_session.refresh(user)

        # Should have deducted only 1 credit
        assert user.credits == 9

    @pytest.mark.asyncio
    async def test_streaming_workflow_without_thumbnails_no_credit_deduction(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that streaming workflow WITHOUT thumbnails doesn't deduct credits."""
        from backend.models.db_models import User
        from sqlalchemy import select

        user_id = authenticated_user["user"]["id"]

        # Give user credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 10
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Mock the workflow service stream generator
        async def mock_stream(*args, **kwargs):
            yield 'data: {"type": "progress", "step": "initializing"}\n\n'
            yield 'data: {"type": "complete"}\n\n'

        with patch('backend.services.workflow_service.WorkflowStreamService.generate_stream') as mock_gen:
            mock_gen.return_value = mock_stream()

            response = await client.post(
                "/generate/full-workflow/stream",
                json={
                    "topic": "Test streaming workflow no thumbs",
                    "enable_thumbnails": False,
                },
                headers=headers,
            )

            # Consume the stream
            async for _ in response.aiter_bytes():
                pass

        # Refresh user from DB
        await db_session.refresh(user)

        # Should NOT have deducted any credits (no thumbnails = no credit charge)
        assert user.credits == 10


class TestDirectThumbnailEndpointStillCharges:
    """Verify that calling thumbnail endpoint directly still charges correctly."""

    @pytest.mark.asyncio
    async def test_direct_thumbnail_call_deducts_credit(
        self, client: AsyncClient, authenticated_user: dict, db_session
    ):
        """Test that calling /generate/thumbnails directly still deducts 1 credit."""
        from backend.models.db_models import User
        from sqlalchemy import select

        user_id = authenticated_user["user"]["id"]

        # Give user credits
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.credits = 10
        await db_session.commit()

        headers = {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}

        # Mock the thumbnail service
        with patch('backend.routers.thumbnail.thumbnail_service') as mock_service:
            mock_service.generate_batch_with_storage = AsyncMock(return_value={
                "success": True,
                "thumbnails": [{"url": "http://test.com/thumb.jpg"}],
                "successful_count": 1,
            })

            response = await client.post(
                "/generate/thumbnails",
                json={
                    "topic": "Direct thumbnail call",
                    "num_thumbnails": 1,
                    "resolution": "1K",
                },
                headers=headers,
            )

        # Refresh user from DB
        await db_session.refresh(user)

        # Should have deducted 1 credit
        assert user.credits == 9

