from src.config import Settings
from src.exporters import MarkdownExporter
from src.feature_flags import FeatureFlags
from src.models import InterviewState, SectionAnswer
from src.providers.registry import build_provider
from src.providers.rule_based import RuleBasedProvider
from src.storage import DisabledStorage, InMemoryStorage, LocalJsonStorage


def test_provider_selection_falls_back_without_claude_key():
    settings = Settings(provider="anthropic", features=FeatureFlags(enable_claude=True), anthropic_api_key=None)
    assert isinstance(build_provider(settings), RuleBasedProvider)


def test_provider_selection_falls_back_when_claude_disabled():
    settings = Settings(provider="anthropic", features=FeatureFlags(enable_claude=False), anthropic_api_key="key")
    assert isinstance(build_provider(settings), RuleBasedProvider)


def test_storage_adapters_round_trip(tmp_path):
    state = InterviewState(sections={"offer": SectionAnswer(section_key="offer", answers=["A useful offer."])})
    memory = InMemoryStorage()
    memory.save_session("s1", state)
    memory.save_brief("s1", "# Brief")
    assert memory.load_session("s1").sections["offer"].combined_answer == "A useful offer."
    assert memory.load_brief("s1") == "# Brief"

    local = LocalJsonStorage(tmp_path)
    local.save_session("s1", state)
    local.save_brief("s1", "# Brief")
    assert local.load_session("s1").sections["offer"].combined_answer == "A useful offer."
    assert local.load_brief("s1") == "# Brief"


def test_disabled_storage_is_safe_noop():
    storage = DisabledStorage()
    storage.save_session("missing", InterviewState())
    storage.save_brief("missing", "# Brief")
    assert storage.load_session("missing") is None
    assert storage.load_brief("missing") is None


def test_markdown_exporter_writes_file(tmp_path):
    exporter = MarkdownExporter()
    output = tmp_path / "brief.md"
    assert exporter.export_text("# Brief") == "# Brief"
    assert exporter.export_file("# Brief", output) == output
    assert output.read_text(encoding="utf-8") == "# Brief"


def test_feature_flag_defaults_keep_mvp_free():
    flags = FeatureFlags()
    assert not flags.enable_claude
    assert not flags.enable_persistence
    assert not flags.enable_analytics
    assert not flags.enable_auth
    assert not flags.enable_pdf_export
