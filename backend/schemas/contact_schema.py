from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum


class PreferredContactMethod(str, Enum):
    phone = "phone"
    email = "email"


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone_number: PhoneNumber
    preferred_contact_method: PreferredContactMethod
    subject: str
    message: str
