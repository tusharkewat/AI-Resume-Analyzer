from starlette.testclient import TestClient


def test_cross_user_isolation(
    client: TestClient,
    auth_headers_user_a,
    auth_headers_user_b,
    sample_pdf_bytes
):
    # User A uploads resume
    res_a = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers_user_a,
        files={"file": ("resume_a.pdf", sample_pdf_bytes, "application/pdf")}
    )
    assert res_a.status_code == 201
    resume_a_id = res_a.json()["id"]

    # User A creates analysis
    analysis_res_a = client.post(
        "/api/v1/analyses",
        headers=auth_headers_user_a,
        json={
            "resume_id": resume_a_id,
            "job_title": "Software Engineer",
            "job_description": "Python, Docker, AWS experience required."
        }
    )
    assert analysis_res_a.status_code == 201
    analysis_a_id = analysis_res_a.json()["id"]

    # --- User B attempts to access User A's resources ---

    # 1. User B tries to get User A's resume -> 403
    res_b_get_resume = client.get(f"/api/v1/resumes/{resume_a_id}", headers=auth_headers_user_b)
    assert res_b_get_resume.status_code == 403

    # 2. User B tries to delete User A's resume -> 403
    res_b_del_resume = client.delete(f"/api/v1/resumes/{resume_a_id}", headers=auth_headers_user_b)
    assert res_b_del_resume.status_code == 403

    # 3. User B tries to run analysis using User A's resume -> 403
    res_b_run_analysis = client.post(
        "/api/v1/analyses",
        headers=auth_headers_user_b,
        json={
            "resume_id": resume_a_id,
            "job_title": "Intruder Role",
            "job_description": "Some job description."
        }
    )
    assert res_b_run_analysis.status_code == 403

    # 4. User B tries to get User A's analysis -> 403
    res_b_get_analysis = client.get(f"/api/v1/analyses/{analysis_a_id}", headers=auth_headers_user_b)
    assert res_b_get_analysis.status_code == 403

    # 5. User B tries to delete User A's analysis -> 403
    res_b_del_analysis = client.delete(f"/api/v1/analyses/{analysis_a_id}", headers=auth_headers_user_b)
    assert res_b_del_analysis.status_code == 403

    # 6. User B tries to download User A's PDF report -> 403
    res_b_download_pdf = client.get(f"/api/v1/analyses/{analysis_a_id}/report", headers=auth_headers_user_b)
    assert res_b_download_pdf.status_code == 403
