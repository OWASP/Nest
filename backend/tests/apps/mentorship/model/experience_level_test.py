from apps.mentorship.models.common.experience_level import ExperienceLevel


class TestExperienceLevel:
    def test_choices(self):
        assert ExperienceLevel.ExperienceLevelChoices.BEGINNER == "beginner"
        assert ExperienceLevel.ExperienceLevelChoices.INTERMEDIATE == "intermediate"
        assert ExperienceLevel.ExperienceLevelChoices.ADVANCED == "advanced"
        assert ExperienceLevel.ExperienceLevelChoices.EXPERT == "expert"
