from starlette.testclient import TestClient


def test_create_and_retrieve_analysis(client: TestClient, auth_headers_user_a, sample_pdf_bytes):
    # 1. Upload resume
    upload_res = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers_user_a,
        files={"file": ("alice_resume.pdf", sample_pdf_bytes, "application/pdf")}
    )
    assert upload_res.status_code == 201
    resume_id = upload_res.json()["id"]

    # 2. Run analysis
    analysis_res = client.post(
        "/api/v1/analyses",
        headers=auth_headers_user_a,
        json={
            "resume_id": resume_id,
            "job_title": "Senior Python Backend Engineer",
            "job_description": "Seeking a Senior Python Engineer with experience in FastAPI, Docker, and PostgreSQL. 3+ years experience required."
        }
    )
    assert analysis_res.status_code == 201
    analysis_data = analysis_res.json()
    assert analysis_data["overall_score"] > 50
    assert len(analysis_data["matching_skills"]) > 0
    assert "score_breakdown" in analysis_data
    assert "recommendations" in analysis_data
    analysis_id = analysis_data["id"]

    # 3. Fetch single analysis
    get_res = client.get(f"/api/v1/analyses/{analysis_id}", headers=auth_headers_user_a)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == analysis_id

    # 4. List analyses
    list_res = client.get("/api/v1/analyses", headers=auth_headers_user_a)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Download PDF report
    pdf_res = client.get(f"/api/v1/analyses/{analysis_id}/report", headers=auth_headers_user_a)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")

    # 6. Dashboard stats
    dash_res = client.get("/api/v1/dashboard/stats", headers=auth_headers_user_a)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_resumes"] >= 1
    assert dash_data["total_analyses"] >= 1
    assert dash_data["average_match_score"] > 0
