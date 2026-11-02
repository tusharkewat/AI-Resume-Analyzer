from app.services.information_extractor import InformationExtractorService


def test_information_extraction():
    sample_text = (
        "Sarah Connor\n"
        "sarah.connor@cyberdyne.org | (555) 321-7654 | Austin, TX\n\n"
        "Professional Summary\n"
        "Lead Infrastructure Engineer with 8 years of experience building resilient cloud platforms.\n\n"
        "Technical Skills\n"
        "Python, Go, Docker, Kubernetes, Terraform, AWS, PostgreSQL, Redis, Linux, CI/CD, Leadership\n\n"
        "Work Experience\n"
        "Principal DevOps Engineer | Cyberdyne Systems | 2018 - 2024\n"
        "- Architected multi-region Kubernetes clusters on AWS.\n"
        "- Automated infrastructure deployment using Terraform and GitHub Actions.\n\n"
        "DevOps Specialist | Resistance Tech | 2016 - 2018\n"
        "- Managed Docker container deployments.\n\n"
        "Education\n"
        "Bachelor of Science in Computer Engineering | Texas A&M | 2016\n"
    )

    data = InformationExtractorService.extract_structured_data(sample_text)

    # Contact check
    assert data.contact.full_name == "Sarah Connor"
    assert data.contact.email == "sarah.connor@cyberdyne.org"
    assert data.contact.phone is not None

    # Summary check
    assert data.summary is not None
    assert "Infrastructure Engineer" in data.summary

    # Skills check
    assert "Python" in data.technical_skills
    assert "Kubernetes" in data.technical_skills
    assert "AWS" in data.technical_skills
    assert "Leadership" in data.soft_skills

    # Experience check
    assert len(data.work_experience) >= 2
    assert data.total_years_experience is not None
    assert data.total_years_experience >= 6

    # Education check
    assert len(data.education) >= 1
    assert "Bachelor" in (data.education[0].degree or "")
