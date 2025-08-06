import pytest
from datetime import timedelta
from django.utils import timezone
from users.models import User
from rest_framework.test import APIClient
from rest_framework import serializers

from polls.models import Poll, PollOption, Vote
from polls.serializers import PollSerializer, PollOptionSerializer, VoteSerializer
from users.serializers import UserSerializer 


@pytest.fixture
def create_test_user():
    """Fixture to create a test user."""
    user = User.objects.create_user(
        username="serializer_test_user",
        email="serializer_test@example.com",
        password="testpassword"
    )
    return user

@pytest.fixture
def create_poll(create_test_user):
    """Fixture to create a poll."""
    user = create_test_user
    closes_at = timezone.now() + timedelta(days=7)
    poll = Poll.objects.create(
        user=user,
        title="Serializer Test Poll",
        description="Description for serializer test.",
        closes_at=closes_at
    )
    return poll

@pytest.fixture
def create_poll_option(create_poll):
    """Fixture to create a poll option."""
    poll = create_poll
    option = PollOption.objects.create(
        poll=poll,
        text="Serializer Option A"
    )
    return option

@pytest.fixture
def create_another_poll_option(create_poll):
    """Fixture to create another poll option for the same poll."""
    poll = create_poll
    option = PollOption.objects.create(
        poll=poll,
        text="Serializer Option B"
    )
    return option

@pytest.fixture
def create_vote(create_poll_option, create_test_user):
    """Fixture to create a vote."""
    option = create_poll_option
    user = create_test_user
    vote = Vote.objects.create(
        option=option,
        user=user
    )
    return vote

@pytest.mark.django_db
class TestPollOptionSerializer:
    def test_serialization(self, create_poll_option):
        """Test PollOption serialization."""
        serializer = PollOptionSerializer(create_poll_option)
        data = serializer.data
        assert data['id'] == create_poll_option.id
        assert data['text'] == create_poll_option.text
        assert 'poll' not in data # Should not include poll ID by default

    def test_deserialization_valid(self, create_poll):
        """Test PollOption deserialization with valid data."""
        data = {'text': 'New Option Text'}
        serializer = PollOptionSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        # Note: PollOptionSerializer typically expects a poll instance during save
        # This test only validates the incoming data structure.
        # The actual creation with a poll instance is handled in PollSerializer's create.

    def test_deserialization_invalid(self):
        """Test PollOption deserialization with invalid data (missing text)."""
        data = {}
        serializer = PollOptionSerializer(data=data)
        assert not serializer.is_valid()
        assert 'text' in serializer.errors

@pytest.mark.django_db
class TestVoteSerializer:
    def test_serialization(self, create_vote):
        """Test Vote serialization."""
        serializer = VoteSerializer(create_vote)
        data = serializer.data
        assert data['id'] == create_vote.id
        assert data['user']['id'] == create_vote.user.id # Assuming UserSerializer is nested
        assert data['option'] == create_vote.option.id # Assuming it's just the ID
        assert 'voted_at' in data

    def test_deserialization_valid(self, create_poll_option, create_test_user):
        """Test Vote deserialization with valid data."""
        data = {
            'option': create_poll_option.id,
            'user': create_test_user.id # In a real scenario, user would be from request.user
        }
        serializer = VoteSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        # The actual save would need to handle the user from request context.

    def test_deserialization_invalid(self):
        """Test Vote deserialization with invalid data (missing fields)."""
        data = {}
        serializer = VoteSerializer(data=data)
        assert not serializer.is_valid()
        assert 'option' in serializer.errors
        assert 'user' in serializer.errors

@pytest.mark.django_db
class TestPollSerializer:
    def test_serialization(self, create_poll, create_poll_option, create_another_poll_option, create_test_user):
        """Test Poll serialization including nested options and votes."""
        # Create a vote for the poll to test votes serialization
        Vote.objects.create(poll_option=create_poll_option, user=create_test_user)

        serializer = PollSerializer(create_poll)
        data = serializer.data

        assert data['id'] == create_poll.id
        assert data['title'] == create_poll.title
        assert data['description'] == create_poll.description
        assert 'created_at' in data
        assert 'closes_at' in data
        assert data['status'] == create_poll.status
        
        # Test nested user serialization
        assert data['user']['id'] == create_poll.user.id
        assert data['user']['username'] == create_poll.user.username

        # Test nested options serialization
        assert len(data['options']) == 2 # Assuming two options were created by fixtures
        assert any(opt['text'] == create_poll_option.text for opt in data['options'])
        assert any(opt['text'] == create_another_poll_option.text for opt in data['options'])

        # Test nested votes serialization
        assert len(data['votes']) == 1 # One vote created
        assert data['votes'][0]['user']['id'] == create_test_user.id


    def test_deserialization_valid_create_with_options(self, create_test_user):
        """Test Poll deserialization and creation with nested options."""
        closes_at = timezone.now() + timedelta(days=7)
        data = {
            'title': 'New Poll with Options',
            'description': 'This poll has options.',
            'closes_at': closes_at.isoformat(),
            'options': [
                {'text': 'Option X'},
                {'text': 'Option Y'}
            ]
        }
        # In a real view, user would be passed via serializer.save(user=request.user)
        # Simulate this by passing it directly to the serializer's create method
        serializer = PollSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)

        # Simulate the perform_create in the view
        poll = serializer.save(user=create_test_user)

        assert poll.id is not None
        assert poll.title == 'New Poll with Options'
        assert poll.user == create_test_user
        assert poll.options.count() == 2
        assert poll.options.filter(text='Option X').exists()
        assert poll.options.filter(text='Option Y').exists()

    def test_deserialization_invalid_missing_title(self):
        """Test Poll deserialization with missing required field."""
        data = {
            'description': 'Missing title.',
            'closes_at': (timezone.now() + timedelta(days=1)).isoformat(),
            'options': [{'text': 'A'}]
        }
        serializer = PollSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_deserialization_invalid_past_closes_at(self):
        """Test Poll deserialization with closes_at in the past."""
        data = {
            'title': 'Invalid Poll',
            'description': 'Closes in the past.',
            'closes_at': (timezone.now() - timedelta(days=1)).isoformat(),
            'options': [{'text': 'A'}]
        }
        serializer = PollSerializer(data=data)
        assert not serializer.is_valid()
        assert 'closes_at' in serializer.errors # Assuming custom validation for past date

    def test_update_poll(self, create_poll):
        """Test updating a poll."""
        new_title = "Updated Poll Title"
        data = {'title': new_title}
        serializer = PollSerializer(create_poll, data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        updated_poll = serializer.save()
        assert updated_poll.title == new_title
        assert updated_poll.id == create_poll.id # Ensure it's the same poll
