from app.logs.trace import get_trace_id, set_trace_id


def test_trace_context_stores_trace_id():
    set_trace_id("abc")

    assert get_trace_id() == "abc"
