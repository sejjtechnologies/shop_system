import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://neondb_owner:npg_e3xRGPCpu2ZE@ep-tiny-bar-abktii0e-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'sejj78ug'  # For sessions/login