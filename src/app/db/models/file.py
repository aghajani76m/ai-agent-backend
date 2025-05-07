class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    filename = Column(String)
    url = Column(String)
    content_type = Column(String)
    size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)