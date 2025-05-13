from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional, Union

# مدل‌های تودرتو برای خوانایی بهتر

class SocialLink(BaseModel):
    platform: str
    url: HttpUrl

class ContactInfo(BaseModel):
    email: Optional[List[EmailStr]] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    socialLinks: Optional[List[SocialLink]] = None

class BasicInfo(BaseModel):
    fullName: str
    contactInfo: Optional[ContactInfo] = None
    profileImage: Optional[HttpUrl] = None # یا str اگر فقط مسیر است
    summery: str

class EducationInstitution(BaseModel):
    name: str
    degree: Optional[str] = None    
    field: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None # می‌تواند "Present" هم باشد
    gpa: Optional[float] = None
    achievements: Optional[List[str]] = None
    location: Optional[str] = None

class Education(BaseModel):
    institutions: List[EducationInstitution] = []

class WorkPosition(BaseModel):
    title: str
    company: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None # می‌تواند "Present" هم باشد
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    location: Optional[str] = None
    keywords: Optional[List[str]] = None

class WorkExperience(BaseModel):
    positions: List[WorkPosition] = []

class SkillDetail(BaseModel):
    name: str
    level: Optional[int] = Field(None, ge=1, le=5) # سطح 1-5
    yearsOfExperience: Optional[Union[int, float]] = None # می‌تواند اعشاری باشد مثل 2.5 سال
    lastUsed: Optional[str] = None # YYYY

class SkillCategory(BaseModel):
    categoryName: str
    skills: List[SkillDetail] = []

class Skills(BaseModel):
    categories: List[SkillCategory] = []

class Certification(BaseModel):
    name: str
    issuer: str
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    credentialId: Optional[str] = None

class ExpectedSalaryRange(BaseModel):
    min: Optional[Union[int,float]] = None # int or float
    max: Optional[Union[int,float]] = None # int or float
    currency: Optional[str] = None

class Availability(BaseModel):
    hoursPerWeek: Optional[int] = None
    preferredWorkType: Optional[List[str]] = None # ["Full-time", "Part-time", "Project-based"]
    immediatelyAvailable: Optional[bool] = None

class WorkPreferences(BaseModel):
    preferredIndustries: Optional[List[str]] = None
    preferredTeamSize: Optional[str] = None
    remoteWork: Optional[bool] = None
    travelPreference: Optional[str] = None

class AiGeneratedMetrics(BaseModel):
    overallExperienceYears: Optional[Union[int,float]] = None
    careerGrowthRate: Optional[float] = Field(None, ge=0, le=1)
    skillDiversity: Optional[float] = Field(None, ge=0, le=1)
    jobStability: Optional[float] = Field(None, ge=0, le=1)
    potentialScore: Optional[float] = Field(None, ge=0, le=1)

class ShadowProfile(BaseModel):
    expertiseLevel: Optional[str] = None # "Junior", "Mid-level", "Senior"
    domainExpertise: Optional[List[str]] = None
    expectedSalaryRange: Optional[ExpectedSalaryRange] = None
    availability: Optional[Availability] = None
    workPreferences: Optional[WorkPreferences] = None
    aiGeneratedMetrics: Optional[AiGeneratedMetrics] = None

class ExtractedResumeData(BaseModel):
    basicInfo: BasicInfo
    education: Education
    workExperience: WorkExperience
    skills: Skills
    certifications: List[Certification] = []
    shadowProfile: ShadowProfile

# مدل نهایی که در API استفاده می‌شود
class ProcessedResumeOutput(BaseModel):
    extractedData: Optional[ExtractedResumeData] = None
    extractedData_persian: Optional[ExtractedResumeData] = None # ساختار مشابه، مقادیر فارسی