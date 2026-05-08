"""
test_advanced_demo.py
=====================
Minh họa các kỹ thuật nâng cao trong Playwright (Python / pytest-playwright):

  1. Làm việc với Frames & Iframe
  2. Quản lý nhiều Windows, Tabs và Popups
  3. Xử lý Dialogs (Alert, Confirm, Prompt)
  4. Tự động hóa Screenshots & Videos khi test failure
  5. Sử dụng Tracing để phân tích chi tiết quá trình thực thi
  6. Hooks: beforeAll / beforeEach / afterEach / afterAll  (pytest: session/function scope fixtures)

Trang demo dùng: file:///.../demo_page.html  (file tĩnh trong repo)
"""

import os
import pathlib
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, expect, sync_playwright

# ─────────────────────────────────────────────
# Đường dẫn tới file HTML demo (đặt cạnh repo)
# ─────────────────────────────────────────────
DEMO_HTML = pathlib.Path(__file__).parents[2] / "demo_page.html"
DEMO_URL   = DEMO_HTML.as_uri()          # file:///…/demo_page.html

# Thư mục lưu screenshots & traces
ARTIFACTS_DIR = pathlib.Path(__file__).parents[2] / "test-artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# ❶  HOOKS – beforeAll / beforeEach / afterEach / afterAll
#    Trong pytest-playwright, hooks được triển khai bằng fixtures có scope:
#      • session  → tương đương beforeAll / afterAll   (chạy 1 lần cho toàn bộ session)
#      • function → tương đương beforeEach / afterEach (chạy trước / sau mỗi test)
# ══════════════════════════════════════════════════════════════════════════════

# ---------- beforeAll / afterAll (session scope) ----------

@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    """
    [Hook – beforeAll / afterAll]
    Chạy MỘT LẦN trước khi bắt đầu toàn bộ test session và sau khi kết thúc.
    Thường dùng để: khởi tạo DB seed, tạo thư mục artifact, in banner log.
    """
    # ── beforeAll ──
    #NNTT: beforeAll chỉ chạy một lần trước khi toàn bộ test suite bắt đầu
    #Nó chạy trước cả beforeEach
    #Mục đích có beforeAll là để khởi tạo môi trường (ví dụ: tạo thư mục artifacts, seed database) cho toàn bộ test suite
    print("\n" + "═" * 60)
    print("  [beforeAll] Bắt đầu test session – khởi tạo môi trường")
    print(f"  Artifacts sẽ được lưu tại: {ARTIFACTS_DIR}")
    print("═" * 60)

    yield   # ← test session chạy ở đây

    # ── afterAll ──
    #NNTT: afterAll chỉ chạy khi toàn bộ test suite hoàn tất và không có lỗi
    # Nếu có lỗi ở bất kỳ test nào trong suite thì afterAll sẽ không chạy
    #Mục đích có afterAll là để dọn dẹp môi trường hoặc ghi log report sau khi toàn bộ test suite hoàn tất
    print("\n" + "═" * 60)
    print("  [afterAll]  Kết thúc test session – dọn dẹp môi trường")
    print("═" * 60)


# ---------- beforeEach / afterEach (function scope) ----------

@pytest.fixture(autouse=True)
def per_test_setup_teardown(request):
    """
    [Hook – beforeEach / afterEach]
    Chạy TRƯỚC và SAU mỗi test function.
    Thường dùng để: reset trạng thái, ghi log tên test, đo thời gian.
    """
    # ── beforeEach ──
    #NNTT: beforeEach chạy trước mỗi test function (không phụ thuộc test khác)
    #Sau khi test function kết thúc, nó sẽ chạy code trong afterEach
    #Mục đích có beforeEach là để reset trạng thái (ví dụ: clear cache, reset DB) cho mỗi test
    print(f"\n  [beforeEach] ▶ Bắt đầu: {request.node.name}")

    yield   # ← test function chạy ở đây

    # ── afterEach ──
    #NNTT: afterEach chạy sau mỗi test function (không phụ thuộc test khác)
    #Trước khi chạy afterEach, nó sẽ chạy code trong beforeEach
    #Mục đích có afterEach là để reset trạng thái (ví dụ: clear cache, reset DB) cho mỗi test
    
    print(f"  [afterEach]  ■ Kết thúc: {request.node.name}")


# ══════════════════════════════════════════════════════════════════════════════
# ❷  SECTION 1 – FRAMES & IFRAMES
# ══════════════════════════════════════════════════════════════════════════════

class TestFramesAndIframes:
    """Kiểm thử tương tác với nội dung bên trong iframe."""

    def test_iframe_01_detect_frame(self, page: Page):
        """
        [Iframe-01] Phát hiện iframe trên trang.
        Kiểm tra rằng phần tử <iframe> hiển thị bằng title của nó (user-facing).
        """
        page.goto(DEMO_URL)
        # Dùng CSS selector cho chính thẻ <iframe> trên trang cha
        # (iframe không có role/text riêng nên dùng locator là hợp lý)
        iframe_element = page.locator("#demo-iframe")
        expect(iframe_element).to_be_visible()

    def test_iframe_02_type_in_frame_input(self, page: Page):
        """
        [Iframe-02] Nhập liệu vào input nằm TRONG iframe – dùng user-facing locator.
        Dùng page.frame_locator() để vào context iframe,
        sau đó dùng get_by_placeholder() thay vì #id selector.
        """
        page.goto(DEMO_URL)
        frame = page.frame_locator("#demo-iframe")
        # User-facing: tìm input qua placeholder text người dùng thấy
        name_input = frame.get_by_placeholder("Enter your name")
        name_input.fill("Playwright Demo")
        expect(name_input).to_have_value("Playwright Demo")

    def test_iframe_02b_fill_without_defining_locator(self, page: Page):
        """
        [Iframe-02b] Fill thẳng vào input nếu không gán Iframe
        """
        page.goto(DEMO_URL)
        page.get_by_placeholder("Enter your name").fill("Direct Fill")
        # Verify cũng chain thẳng -> testcase vẫn passed bình thường. 
        expect(
            page.get_by_placeholder("Enter your name")
        ).to_have_value("Direct Fill")

    def test_iframe_03_click_button_inside_frame(self, page: Page):
        """
        [Iframe-03] Click button bên trong iframe và xác minh output.
        Dùng get_by_role("button") thay vì #id selector cho button Submit.
        """
        page.goto(DEMO_URL)
        frame = page.frame_locator("#demo-iframe")
        # User-facing: tìm input qua placeholder, button qua role + name
        frame.get_by_placeholder("Enter your name").fill("Nhung")
        frame.get_by_role("button", name="Submit").click()
        # Xác minh kết quả bằng get_by_text (text người dùng thấy)
        expect(frame.get_by_text("Hello, Nhung!")).to_be_visible()

    def test_iframe_04_clear_and_resubmit(self, page: Page):
        """
        [Iframe-04] Xóa dữ liệu trong iframe input và submit lại.
        Toàn bộ dùng user-facing locators: get_by_placeholder, get_by_role, get_by_text.
        """
        page.goto(DEMO_URL)
        frame = page.frame_locator("#demo-iframe")
        inp = frame.get_by_placeholder("Enter your name")
        inp.fill("OldName")
        inp.clear()
        inp.fill("NewName")
        frame.get_by_role("button", name="Submit").click()
        expect(frame.get_by_text("Hello, NewName!")).to_be_visible()

    def test_iframe_04_nested_correct(self, page: Page):
        """
        [Iframe-04 ✅] Click "Click button" trong Iframe C (tầng 3) – cách ĐÚNG.
        Cả 3 iframe đều có button tên "Click button".
        Phải chain đúng tầng mới click đúng button trong iframe C.
        """
        page.goto(DEMO_URL)
        page.locator("#btn-open-nested").click()

        frame_A = page.frame_locator("#iframe-A")
        frame_A.locator("#btn-open-B").click()

        frame_B = frame_A.frame_locator("#iframe-B")
        frame_B.locator("#btn-open-C").click()

        # ✅ Đúng: vào đúng frame_C mới click được "Click button" của iframe C
        frame_C = frame_B.frame_locator("#iframe-C")
        frame_C.get_by_role("button", name="Click button").click()
        expect(frame_C.get_by_text("Clicked C!")).to_be_visible()

    def test_iframe_04b_nested_wrong(self, page: Page):
        """
        [Iframe-04b ❌] Click "Click button" KHÔNG khai báo frame → FAIL.
        Cả 3 iframe đều có button tên "Click button".
        Nếu chỉ gọi page.get_by_role("button", name="Click button")
        → Playwright không tìm thấy vì button nằm trong iframe, không phải main page.
        """
        page.goto(DEMO_URL)
        page.locator("#btn-open-nested").click()

        frame_A = page.frame_locator("#iframe-A")
        frame_A.locator("#btn-open-B").click()

        frame_B = frame_A.frame_locator("#iframe-B")
        frame_B.locator("#btn-open-C").click()

        # ❌ Sai: gọi thẳng từ page mà không vào frame_C
        # Dù button tên "Click button" tồn tại ở cả 3 iframe,
        # page không thể tìm thấy bất kỳ button nào vì chúng đều nằm trong iframe.
        page.get_by_role("button", name="Click button").click()
        expect(page.get_by_text("Clicked C!")).to_be_visible()


# ══════════════════════════════════════════════════════════════════════════════
# ❸  SECTION 2 – WINDOWS, TABS & POPUPS
# ══════════════════════════════════════════════════════════════════════════════

class TestWindowsTabsPopups:
    """Kiểm thử mở tab mới, popup window, và modal nội trang."""

    def test_tab_01_open_new_tab_and_switch(self, context: BrowserContext, page: Page):
        """
        [Tab-01] Mở tab mới khi click nút 'Open New Tab'.
        Playwright lắng nghe sự kiện 'page' trên context để bắt tab mới.
        Kiểm tra URL của tab mới chứa 'playwright.dev'.
        """
        page.goto(DEMO_URL)
        # Lắng nghe tab mới được mở
        with context.expect_page() as new_page_info:
            page.locator("#btn-new-tab").click()
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        assert "playwright.dev" in new_page.url, (
            f"Expected playwright.dev in URL, got: {new_page.url}"
        )
        new_page.close()

    def test_tab_02_main_page_still_active_after_new_tab(self, context: BrowserContext, page: Page):
        """
        [Tab-02] Sau khi mở tab mới, trang chính vẫn giữ nguyên trạng thái.
        Kiểm tra section iframe vẫn hiển thị trên trang gốc.
        """
        page.goto(DEMO_URL)
        with context.expect_page():
            page.locator("#btn-new-tab").click()
        expect(page.locator("#section-iframe")).to_be_visible()

    def test_popup_01_open_popup_window(self, context: BrowserContext, page: Page):
        """
        [Popup-01] Mở Popup Window qua window.open() với kích thước cố định.
        Bắt popup bằng context.expect_page() và xác minh nó được load.
        """
        page.goto(DEMO_URL)
        with context.expect_page() as popup_info:
            page.locator("#btn-popup").click()
        popup = popup_info.value
        popup.wait_for_load_state()
        assert popup is not None
        popup.close()

    def test_modal_01_open_close_internal_modal(self, page: Page):
        """
        [Modal-01] Mở modal nội trang và đóng bằng nút Cancel.
        Modal là overlay CSS (không phải cửa sổ mới) – kiểm tra hiển thị / ẩn.
        """
        page.goto(DEMO_URL)
        page.locator("#btn-internal-modal").click()
        modal = page.locator("#modal-overlay")
        expect(modal).to_be_visible()
        page.locator("#modal-cancel-btn").click()
        expect(modal).to_be_hidden()
    
    def test_modal_01b_open_close_internal_modal(self, page: Page):
        """
        [Modal-01b] Mở modal mà không define rõ ra
        """
        page.goto(DEMO_URL)
        page.locator("#btn-internal-modal").click()
        page.locator("#modal-cancel-btn").click()
        expect(page.locator("#modal-cancel-btn")).to_be_hidden()

    def test_modal_02_confirm_modal_with_input(self, page: Page):
        """
        [Modal-02] Nhập text vào modal rồi click Confirm.
        Sau khi confirm, text nhập phải xuất hiện trong #modal-result.
        """
        page.goto(DEMO_URL)
        page.locator("#btn-internal-modal").click()
        page.locator("#modal-input").fill("TestUser")
        page.locator("#modal-confirm-btn").click()
        expect(page.locator("#modal-result")).to_contain_text("TestUser")


# ══════════════════════════════════════════════════════════════════════════════
# ❹  SECTION 3 – DIALOGS (Alert, Confirm, Prompt)
# ══════════════════════════════════════════════════════════════════════════════

class TestDialogs:
    """Kiểm thử xử lý browser native dialogs: alert, confirm, prompt."""

    # ── helper dùng chung: đăng ký handler rồi click trigger ──────────────
    def _trigger(self, page: Page, btn_id: str, handler):
        """Goto demo → đăng ký dialog handler → click nút trigger."""
        page.goto(DEMO_URL)
        page.on("dialog", handler)
        page.get_by_role("button", name=btn_id).click()
        page.wait_for_timeout(400)

    # ── tests ──────────────────────────────────────────────────────────────

    def test_dialog_01_alert_accept(self, page: Page):
        """
        [Dialog-01] Alert: accept (OK) và kiểm tra type + message.
        Dùng list để capture vì lambda không thể gán vào dict.
        """
        captured = []
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: (captured.append((d.type, d.message)), d.accept()))
        page.get_by_role("button", name="🔔 Trigger Alert").click()
        page.wait_for_timeout(400)

        assert captured[0][0] == "alert"
        assert "Alert dialog" in captured[0][1]

    def test_dialog_02_confirm_accept(self, page: Page):
        """[Dialog-02] Confirm: accept → UI hiển thị 'Confirmed'."""
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: d.accept())
        page.get_by_role("button", name="❓ Trigger Confirm").click()
        expect(page.locator("#confirm-result")).to_contain_text("Confirmed")

    def test_dialog_03_confirm_dismiss(self, page: Page):
        """[Dialog-03] Confirm: dismiss → UI hiển thị 'Cancelled'."""
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: d.dismiss())
        page.get_by_role("button", name="❓ Trigger Confirm").click()
        expect(page.locator("#confirm-result")).to_contain_text("Cancelled")

    def test_dialog_04_prompt_accept_with_text(self, page: Page):
        """[Dialog-04] Prompt: accept với text → text xuất hiện trong #prompt-result."""
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: d.accept("Automation Tester"))
        page.get_by_role("button", name="✏️ Trigger Prompt").click()
        expect(page.locator("#prompt-result")).to_contain_text("Automation Tester")

    def test_dialog_05_prompt_dismiss(self, page: Page):
        """[Dialog-05] Prompt: dismiss → UI hiển thị thông báo 'dismissed'."""
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: d.dismiss())
        page.get_by_role("button", name="✏️ Trigger Prompt").click()
        page.wait_for_timeout(500)

        expect(page.locator("#prompt-result")).to_contain_text("dismissed")


# ══════════════════════════════════════════════════════════════════════════════
# ❺  SECTION 4 – SCREENSHOTS & VIDEOS khi test failure
# ══════════════════════════════════════════════════════════════════════════════

class TestScreenshotsAndVideos:
    """
    Minh họa chụp ảnh màn hình thủ công và tự động khi test thất bại.

    ── Cách bật video ──────────────────────────────────────────────────────────
    Cấu hình trong pytest.ini (đã set sẵn):
        --video=retain-on-failure   → chỉ giữ video khi test FAIL (tiết kiệm disk)
        --video=on                  → quay video cho TẤT CẢ test
        --video=off                 → tắt hoàn toàn
        --screenshot=only-on-failure → chụp ảnh khi FAIL

    ── Video được lưu ở đâu? ───────────────────────────────────────────────────
    pytest-playwright tự lưu vào: test-results/<test-name>/video.webm
    conftest.py có hook copy thêm vào: test-artifacts/<test-name>.webm

    ── Xem video ───────────────────────────────────────────────────────────────
    Mở file .webm bằng trình duyệt hoặc VLC.
    Hoặc xem qua pytest-html report (đã được nhúng tự động).

    ── Fixture capture_on_failure ───────────────────────────────────────────────
    Fixture này chạy afterEach, tự động:
      1. Chụp screenshot thủ công khi test FAIL
      2. Lưu vào test-artifacts/<test_name>.png
    """

    @pytest.fixture(autouse=True)
    def capture_on_failure(self, page: Page, request):
        """
        [Hook – afterEach] Tự động chụp ảnh và lấy path video khi test FAIL.
        """
        ### NNTT: Hook này chạy tự động cho mỗi test.
        yield   # Chờ test function chạy xong.

        # Kiểm tra xem test case vừa rồi có bị FAIL hay không.
        failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
        if not failed:
            return

        # 1. Xử lý Screenshot (Chụp và lưu file ngay lập tức)
        screenshot_path = ARTIFACTS_DIR / f"{request.node.name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"\n  📸 Screenshot: {screenshot_path}")

        # 2. Xử lý Video
        # Lấy thông tin video từ object page.
        video = page.video
        if video:
            # Lưu ý: Video chỉ thực sự được lưu vào đĩa sau khi Browser Context đóng.
            # Dòng print này giúp bạn biết file video sẽ nằm ở đâu.
            try:
                print(f"  🎥 Video path: {video.path()}")
            except Exception:
                print("  🎥 Video đang được xử lý (sẽ có sau khi đóng browser)...")

    def test_screenshot_01_manual_screenshot(self, page: Page):
        """
        [Screenshot-01] Chụp ảnh màn hình thủ công (manual screenshot).
        Điều hướng đến trang demo → chụp toàn trang → kiểm tra file tồn tại.
        """
        page.goto(DEMO_URL)
        out = ARTIFACTS_DIR / "manual_full_page.png"
        page.screenshot(path=str(out), full_page=True)
        assert out.exists(), "Screenshot file không được tạo!"

    def test_screenshot_02_element_screenshot(self, page: Page):
        """
        [Screenshot-02] Chụp ảnh một phần tử cụ thể (element screenshot).
        Chỉ chụp section dialog thay vì toàn trang.
        """
        page.goto(DEMO_URL)
        out = ARTIFACTS_DIR / "element_section_dialogs.png"
        page.locator("#section-dialogs").screenshot(path=str(out))
        assert out.exists(), "Element screenshot không được tạo!"

    def test_screenshot_03_video_on_failure_demo(self, page: Page):
        """
        [Screenshot-03] ★ DEMO VIDEO KHI FAIL ★

        Test này CỐ TÌNH FAIL để minh họa:
          • pytest-playwright tự quay video (--video=retain-on-failure)
          • Fixture capture_on_failure chụp ảnh + nhúng vào report
          • File video .webm được lưu trong thư mục test-results/

        ── Cách chạy để xem video ──────────────────────────────────────────────
        Chạy lệnh:  pytest tests/demo_automation/test_advanced_demo.py::TestScreenshotsAndVideos::test_screenshot_03_video_on_failure_demo
        Sau khi chạy xong:
          → Mở thư mục test-results/ → tìm folder tên test → mở video.webm
          → Hoặc mở pytest-report.html → click vào test FAILED → xem video nhúng

        Luồng thao tác trước khi fail:
          1. Mở trang demo
          2. Click nút Simulate Failure State
          3. Nhập vào modal
          4. Assert sai → FAIL → video + screenshot được giữ lại
        """
        page.goto(DEMO_URL)

        # Bước 1: click simulate failure (có thể thấy trong video)
        page.get_by_role("button", name="💥 Simulate Failure State").click()
        page.wait_for_timeout(600)

        # Bước 2: mở modal, nhập text
        page.get_by_role("button", name="💬 Open In-page Modal").click()
        page.locator("#modal-input").fill("This will fail")
        page.wait_for_timeout(600)

        # Bước 3: assert SAI CỐ TÌNH → test FAIL
        # → pytest-playwright giữ lại video (do --video=retain-on-failure trong pytest.ini)
        # → fixture capture_on_failure chụp screenshot trạng thái lỗi
        # → Cả video lẫn screenshot đều xuất hiện trong pytest-report.html
        expect(page.locator("#modal-result")).to_contain_text(
            "WRONG_TEXT_TO_FORCE_FAILURE",
            timeout=2000
        )

# Pytest hook để đánh dấu kết quả call vào node (dùng cho capture_on_failure)
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Gắn kết quả (passed/failed) vào test node để fixture có thể đọc."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ══════════════════════════════════════════════════════════════════════════════
# ❻  SECTION 5 – TRACING
# ══════════════════════════════════════════════════════════════════════════════

class TestTracing:
    """
    Minh họa Playwright Tracing – ghi lại toàn bộ network, DOM snapshot,
    console log và screenshots trong quá trình test để phân tích sau.

    Xem trace:  npx playwright show-trace <file.zip>
    """

    def test_tracing_01_record_full_trace(self, browser: Browser):
        """
        [Tracing-01] Bật trace, thực hiện một luồng thao tác, dừng trace và lưu file .zip.
        Trace bao gồm: screenshots, snapshots, sources.
        Kiểm tra file trace được tạo ra.
        """
        context = browser.new_context()
        # Bật tracing với đầy đủ tùy chọn
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()
        page.goto(DEMO_URL)
        page.locator("#btn-trace-submit").click()   # tương tác để trace ghi lại

        trace_path = str(ARTIFACTS_DIR / "trace_full.zip")
        context.tracing.stop(path=trace_path)
        context.close()

        assert pathlib.Path(trace_path).exists(), "Trace file không được tạo!"
        ### Lệnh mở trace:
        # npx playwright show-trace test-artifacts/trace_full.zip
    def test_tracing_02_trace_form_submission(self, browser: Browser):
        """
        [Tracing-02] Trace một luồng điền form và submit.
        Điền tên + email trong section Tracing → submit → dừng trace.
        Hữu ích để phân tích tại sao form không submit đúng.
        """
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True)

        page = context.new_page()
        page.goto(DEMO_URL)

        # Điền form
        page.locator("#trace-name").fill("Test User")
        page.locator("#trace-email").fill("test@example.com")
        page.locator("#btn-trace-submit").click()

        # Xác minh kết quả
        expect(page.locator("#trace-result")).to_contain_text("Done Submit")

        trace_path = str(ARTIFACTS_DIR / "trace_form_submit.zip")
        context.tracing.stop(path=trace_path)
        context.close()

        assert pathlib.Path(trace_path).exists()

    def test_tracing_03_trace_dialog_interaction(self, browser: Browser):
        """
        [Tracing-03] Trace tương tác với dialog.
        Ghi lại toàn bộ quá trình mở và xử lý Confirm dialog.
        """
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True)

        page = context.new_page()
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: d.accept())
        page.locator("#btn-confirm").click()
        page.wait_for_timeout(400)

        trace_path = str(ARTIFACTS_DIR / "trace_dialog.zip")
        context.tracing.stop(path=trace_path)
        context.close()

        assert pathlib.Path(trace_path).exists()

    def test_tracing_04_trace_iframe_interaction(self, browser: Browser):
        """
        [Tracing-04] Trace tương tác với iframe.
        Ghi lại quá trình nhập liệu và submit form bên trong iframe.
        """
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True)

        page = context.new_page()
        page.goto(DEMO_URL)

        frame = page.frame_locator("#demo-iframe")
        frame.locator("#iframe-name").fill("Tracing Inside Iframe")
        frame.locator("#iframe-submit-btn").click()

        trace_path = str(ARTIFACTS_DIR / "trace_iframe.zip")
        context.tracing.stop(path=trace_path)
        context.close()

        assert pathlib.Path(trace_path).exists()
    
    def test_tracing_05_trace_alert(self, browser: Browser):
        """
        [Tracing-05] Trace tương tác với alert.
        Ghi lại toàn bộ quá trình mở và xử lý Alert.
        """
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True)

        page = context.new_page()
        page.goto(DEMO_URL)
        page.on("dialog", lambda d: d.accept())
        page.get_by_role("button", name="❓ Trigger Confirm").click()
        expect(page.locator("#confirm-result")).to_contain_text("Confirmed")

        trace_path = str(ARTIFACTS_DIR / "trace_alert.zip")
        context.tracing.stop(path=trace_path)
        context.close()

        assert pathlib.Path(trace_path).exists()
