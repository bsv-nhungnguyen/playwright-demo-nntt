from pages.base_page import BasePage
from pages.login_page import LoginPage
import pytest

URL = "https://playwright-demo.eventos.work/web/portal/529/event/3988/users/login"


@pytest.fixture
def access_to_login_page(page):
    login_page = LoginPage(page)
    login_page.navigate(URL)
    return login_page


# ──────────────────────────────────────────────────────────────────────────────
# Khi test FAIL: copy video.webm vào test-artifacts/ để dễ tìm
#
# pytest-playwright --video=retain-on-failure tự động:
#   1. Quay video suốt test
#   2. Khi FAIL → move file vào: test-results/<test-folder>/video.webm
#   3. Khi PASS → xóa video
#
# Hook bên dưới tìm file video.webm đó và copy vào test-artifacts/
# ──────────────────────────────────────────────────────────────────────────────
import pathlib, shutil

ARTIFACTS_DIR = pathlib.Path("test-artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

_failed_nodeids: set = set()   # track nodeid bị fail


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Phase 'call'     → đánh dấu test bị fail
    Phase 'teardown' → tìm video.webm trong test-results/ và copy vào test-artifacts/
    """
    outcome = yield
    report = outcome.get_result()

    # ── CALL phase: đánh dấu test fail ──────────────────────────────────────
    if report.when == "call" and report.failed:
        _failed_nodeids.add(item.nodeid)

    # ── TEARDOWN phase: tìm và copy video ────────────────────────────────────
    elif report.when == "teardown" and item.nodeid in _failed_nodeids:
        _failed_nodeids.discard(item.nodeid)

        # pytest-playwright đặt tên folder từ nodeid, thay :: và / bằng -
        # Ví dụ: tests/demo/test_foo.py::Class::test_bar[chromium]
        #      → tests-demo-test-foo-py-class-test-bar-chromium
        folder_name = (
            item.nodeid
            .replace("/", "-")
            .replace("\\", "-")
            .replace("::", "-")
            .replace("[", "-")
            .replace("]", "")
            .replace(".", "-")
            .replace("_", "-")   # underscore → dash (pytest-playwright convention)
            .lower()
        )

        test_results = pathlib.Path("test-results")
        # Tìm folder khớp (pytest-playwright có thể thêm suffix số)
        matches = list(test_results.glob(f"{folder_name}*/video.webm"))
        if not matches:
            return

        video_src = matches[-1]   # lấy file mới nhất nếu có nhiều
        safe_name = item.nodeid.split("::")[-1].replace("[", "_").replace("]", "")
        dest = ARTIFACTS_DIR / f"{safe_name}.webm"
        try:
            shutil.copy2(video_src, dest)
            print(f"\n  🎬 Video → test-artifacts/{dest.name}")
        except Exception as e:
            print(f"\n  ⚠️ Video copy failed: {e}")