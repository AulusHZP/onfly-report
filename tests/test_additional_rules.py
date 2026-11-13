"""Additional report tests."""

from helpers import run_cli


def test_more_than_200_rows(tmp_path):
    rows = []
    for number in range(205):
        rows.append({"reservation_id": f"R-{number}"})

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_reservations"] == 205
    assert report["summary"]["confirmed_reservations"] == 205
    assert report["summary"]["total_room_nights"] == 205
    assert report["summary"]["total_amount_brl"] == "20500.00"
    assert report["by_month"][0]["reservations"] == 205
    assert report["top_hotels"][0]["total_brl"] == "20500.00"


def test_leap_year(tmp_path):
    rows = [
        {"checkin_date": "2024-02-28", "checkout_date": "2024-03-01", "rooms": "2"}
    ]
    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_room_nights"] == 4
    assert report["by_month"][0]["room_nights"] == 4
    assert report["top_hotels"][0]["room_nights"] == 4


def test_year_change(tmp_path):
    rows = [
        {"checkin_date": "2024-12-30", "checkout_date": "2025-01-02", "rooms": "2"}
    ]
    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_room_nights"] == 6
    assert report["by_month"][0]["room_nights"] == 6
    assert report["top_hotels"][0]["room_nights"] == 6


def test_round_after_sum(tmp_path):
    rows = [
        {"reservation_id": "R-1", "currency": "USD", "amount": "0.01"},
        {"reservation_id": "R-2", "currency": "USD", "amount": "0.01"},
        {"reservation_id": "R-3", "currency": "USD", "amount": "0.01"},
    ]
    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_amount_brl"] == "0.16"
    assert report["summary"]["average_nightly_rate_brl"] == "0.05"
    assert report["by_month"][0]["total_brl"] == "0.16"
    assert report["top_hotels"][0]["total_brl"] == "0.16"


def test_half_up(tmp_path):
    report = run_cli(tmp_path, [{"amount": "1.005"}])

    assert report["summary"]["total_amount_brl"] == "1.01"
    assert report["summary"]["average_nightly_rate_brl"] == "1.01"
    assert report["by_month"][0]["total_brl"] == "1.01"
    assert report["top_hotels"][0]["total_brl"] == "1.01"


def test_hotel_tie(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B"},
            {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A"},
        ],
    )

    hotels = report["top_hotels"]
    assert len(hotels) == 2
    assert hotels[0]["hotel_id"] == "H01"
    assert hotels[1]["hotel_id"] == "H02"


def test_only_confirmed(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CONFIRMED", "hotel_id": "H01"},
            {
                "reservation_id": "R-2",
                "status": "CANCELLED",
                "hotel_id": "H02",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-11",
            },
            {
                "reservation_id": "R-3",
                "status": "NO_SHOW",
                "hotel_id": "H03",
                "checkin_date": "2025-03-10",
                "checkout_date": "2025-03-11",
            },
        ],
    )

    assert report["summary"] == {
        "total_reservations": 3,
        "confirmed_reservations": 1,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 1,
        "total_amount_brl": "100.00",
        "average_nightly_rate_brl": "100.00",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "100.00"}
    ]
    assert len(report["top_hotels"]) == 1
    assert report["top_hotels"][0]["hotel_id"] == "H01"


def test_empty_file(tmp_path):
    report = run_cli(tmp_path, [])

    assert report["summary"] == {
        "total_reservations": 0,
        "confirmed_reservations": 0,
        "cancelled_reservations": 0,
        "no_show_reservations": 0,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []
    assert report["report_version"] == "1.0"
    assert report["generated_at"].endswith("-03:00")


def test_month_order(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-2", "checkin_date": "2025-02-02", "checkout_date": "2025-02-03"},
            {"reservation_id": "R-1", "checkin_date": "2025-01-30", "checkout_date": "2025-02-02"},
        ],
    )

    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 3, "total_brl": "100.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 1, "total_brl": "100.00"},
    ]
