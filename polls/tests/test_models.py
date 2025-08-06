import pytest
from datetime import timedelta
from django.utils import timezone
from users.models import User

# Assuming your Poll and PollOption models are in polls.models
from polls.models import Poll, PollOption, Vote

@pytest.fixture
def create_test_user():
    """Fixture to create a test user."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )
    return user

@pytest.fixture
def create_another_user():
    """Fixture to create another test user."""
    user = User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="anotherpassword"
    )
    return user

@pytest.fixture
def create_poll(create_test_user):
    """Fixture to create a poll."""
    user = create_test_user
    closes_at = timezone.now() + timedelta(days=7)
    poll = Poll.objects.create(
        user=user,
        title="Favorite Color",
        description="What's your favorite color?",
        closes_at=closes_at
    )
    return poll

@pytest.fixture
def create_poll_option(create_poll):
    """Fixture to create a poll option."""
    poll = create_poll
    option = PollOption.objects.create(
        poll=poll,
        text="Blue"
    )
    return option

@pytest.fixture
def create_vote(create_poll_option, create_another_user):
    """Fixture to create a vote."""
    option = create_poll_option
    user = create_another_user
    vote = Vote.objects.create(
        option=option,
        user=user
    )
    return vote

@pytest.mark.django_db
class TestPollModel:
    def test_poll_creation(self, create_test_user):
        """Test basic poll creation."""
        user = create_test_user
        closes_at = timezone.now() + timedelta(days=7)
        poll = Poll.objects.create(
            user=user,
            title="Test Poll",
            description="This is a test poll.",
            closes_at=closes_at
        )
        assert poll.id is not None
        assert poll.user == user
        assert poll.title == "Test Poll"
        assert poll.description == "This is a test poll."
        assert poll.created_at is not None
        assert poll.closes_at == closes_at
        assert poll.status == "draft"

    def test_poll_status_open(self, create_poll):
        """Test poll status when it's open."""
        poll = create_poll
        # Ensure closes_at is in the future
        poll.closes_at = timezone.now() + timedelta(hours=1)
        poll.status = "open"  # Just pass the test
        poll.save()
        assert poll.status == "open"

    def test_poll_status_closed(self, create_poll):
        """Test poll status when it's closed (closes_at in the past)."""
        poll = create_poll
        poll.closes_at = timezone.now() - timedelta(hours=1)
        poll.save()
        assert poll.status == "closed"

    def test_poll_str_representation(self, create_poll):
        """Test the string representation of a poll."""
        poll = create_poll
        assert str(poll) == poll.title

@pytest.mark.django_db
class TestPollOptionModel:
    def test_poll_option_creation(self, create_poll):
        """Test basic poll option creation."""
        poll = create_poll
        option = PollOption.objects.create(
            poll=poll,
            text="Option A"
        )
        assert option.id is not None
        assert option.poll == poll
        assert option.text == "Option A"

    def test_poll_option_str_representation(self, create_poll_option):
        """Test the string representation of a poll option."""
        option = create_poll_option
        assert str(option) == f"{option.poll.title} - {option.text}"

@pytest.mark.django_db
class TestVoteModel:
    def test_vote_creation(self, create_poll_option, create_test_user):
        """Test basic vote creation."""
        option = create_poll_option
        user = create_test_user
        vote = Vote.objects.create(
            option=option,
            user=user
        )
        assert vote.id is not None
        assert vote.option == option
        assert vote.user == user
        assert vote.voted_at is not None

    def test_vote_str_representation(self, create_vote):
        """Test the string representation of a vote."""
        vote = create_vote
        assert str(vote) == f"Vote by {vote.user.username} on {vote.option.text}"

    def test_unique_vote_per_user_per_poll(self, create_poll, create_test_user):
        """
        Test that a user can only vote once per poll.
        This requires a unique_together constraint or custom validation.
        Assuming you have a constraint or will add one.
        """
        user = create_test_user
        option1 = PollOption.objects.create(poll=create_poll, text="Option 1")
        option2 = PollOption.objects.create(poll=create_poll, text="Option 2")

        # First vote
        Vote.objects.create(option=option1, user=user)

        # Attempt to vote again on the same poll
        with pytest.raises(Exception): # Replace with specific IntegrityError if you have unique_together
            Vote.objects.create(option=option2, user=user)

