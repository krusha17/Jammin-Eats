import sqlite3
import pytest
import pygame
from pathlib import Path

# Initialize pygame for font usage
@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()

# Import DAL functions and states after pygame init
import src.persistence.dal as dal
from src.states.tutorial_state import TutorialState
from src.states.tutorial_complete_state import TutorialCompleteState
from src.states.title_state import TitleState

class DummyGame:
    def __init__(self):
        self.successful_deliveries = 0
        self.money = 0
        self.tutorial_mode = True
        self.tutorial_completed = False

# Setup a temporary SQLite DB with player_profile table including tutorial_complete
@pytest.fixture(autouse=True)
def patch_db_path(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE player_profile (
            player_id INTEGER PRIMARY KEY,
            display_name TEXT,
            high_score INTEGER,
            tutorial_complete INTEGER DEFAULT 0
        );
    """)
    # Insert default profile (tutorial_complete defaults to 0)
    cursor.execute(
        "INSERT INTO player_profile (player_id, display_name, high_score) VALUES (1, 'Player', 0)"
    )
    conn.commit()
    conn.close()
    # Patch the DB_PATH in the DAL module
    monkeypatch.setattr(dal, "DB_PATH", db_file)
    return db_file

# --- Unit Tests: DAL ---

def test_is_tutorial_complete_default_false():
    assert dal.is_tutorial_complete() is False


def test_mark_tutorial_complete_sets_flag():
    assert dal.mark_tutorial_complete() is True
    assert dal.is_tutorial_complete() is True

# --- Unit Tests: TutorialState ---

def test_tutorial_state_no_transition_initially():
    game = DummyGame()
    ts = TutorialState(game)
    assert getattr(ts, 'next_state', None) is None


def test_tutorial_state_transition_on_deliveries():
    game = DummyGame()
    ts = TutorialState(game)
    game.successful_deliveries = ts.target_deliveries
    game.money = 0
    ts.update(0.1)
    assert isinstance(ts.next_state, TutorialCompleteState)


def test_tutorial_state_transition_on_money():
    game = DummyGame()
    ts = TutorialState(game)
    game.successful_deliveries = 0
    game.money = ts.target_money
    ts.update(0.1)
    assert isinstance(ts.next_state, TutorialCompleteState)

# --- Unit Tests: TutorialCompleteState ---

def test_tutorial_complete_state_handle_event_enters_title(monkeypatch):
    # Track if mark_tutorial_complete is called
    called = {'flag': False}
    def fake_mark(pid=1):
        called['flag'] = True
        return True
    monkeypatch.setattr(dal, 'mark_tutorial_complete', fake_mark)
    game = DummyGame()
    tcs = TutorialCompleteState(game)
    # Simulate ENTER key
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    handled = tcs.handle_event(event)
    assert handled is True
    assert called['flag'] is True
    assert isinstance(tcs.next_state, TitleState)

# --- Unit Tests: TitleState ---

def test_title_state_continue_disabled_when_tutorial_incomplete(monkeypatch):
    monkeypatch.setattr(dal, 'is_tutorial_complete', lambda pid=1: False)
    game = DummyGame()
    title = TitleState(game)
    # Continue is first menu item
    assert title.menu_items[0]['enabled'] is False


def test_title_state_continue_enabled_when_tutorial_complete(monkeypatch):
    monkeypatch.setattr(dal, 'is_tutorial_complete', lambda pid=1: True)
    game = DummyGame()
    title = TitleState(game)
    assert title.menu_items[0]['enabled'] is True
