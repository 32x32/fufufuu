from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Boolean, Float

Base = declarative_base()


class OldUser(Base):

    __tablename__ = 'account_user'

    id                  = Column(Integer, primary_key=True)
    username            = Column(String)
    password            = Column(String)
    permission_flags    = Column(String)
    description         = Column(String)
    picture             = Column(String)
    last_login          = Column(DateTime)
    date_joined         = Column(DateTime)
    is_staff            = Column(Boolean)
    is_active           = Column(Boolean)


class OldComment(Base):

    __tablename__ = 'comment_comment'

    id                  = Column(Integer, primary_key=True)
    content_type_id     = Column(Integer)
    object_pk           = Column(String)
    user_id             = Column(Integer)
    comment             = Column(String)
    upvotes             = Column(Integer)
    downvotes           = Column(Integer)
    score               = Column(Float)
    ip_address          = Column(String)
    date_created        = Column(DateTime)



class OldManga(Base):

    __tablename__ = 'manga_manga'

    id                  = Column(Integer, primary_key=True)
    uploader_id         = Column(Integer)
    title               = Column(String)
    slug                = Column(String)
    descriptpion        = Column(String)
    cover               = Column(String)
    category            = Column(String)
    language            = Column(String)
    status              = Column(String)
    zip                 = Column(String)
    tank_id             = Column(Integer)
    tank_chp            = Column(String)
    comment_count       = Column(Integer)
    favorite_count      = Column(Integer)
    download_count      = Column(Integer)
    date_created        = Column(DateTime)
    last_updated        = Column(DateTime)
    date_published      = Column(DateTime)


class OldMangaFavoriteUser(Base):

    __tablename__ = 'manga_manga_favorite_users'

    id                  = Column(Integer, primary_key=True)
    manga_id            = Column(Integer)
    user_id             = Column(Integer)


class OldMangaTag(Base):

    __tablename__ = 'manga_manga_tags'

    id                  = Column(Integer, primary_key=True)
    manga_id            = Column(Integer)
    tag_id              = Column(Integer)


class OldMangaPage(Base):

    __tablename__ = 'manga_mangapage'

    id                  = Column(Integer, primary_key=True)
    manga_id            = Column(Integer)
    double              = Column(Boolean)
    page                = Column(Integer)
    image_source        = Column(String)
    image_thumb         = Column(String)
    image_small         = Column(String)
    image_smalld        = Column(String)
    date_created        = Column(DateTime)
    name                = Column(String)


class OldTag(Base):

    __tablename__ = 'tag_tag'

    id                  = Column(Integer, primary_key=True)
    tag_type            = Column(String)
    name                = Column(String)
    slug                = Column(String)
    url                 = Column(String)
    manga_count         = Column(Integer)
    date_created        = Column(DateTime)


class OldTank(Base):

    __tablename__ = 'tank_tank'

    id                  = Column(Integer, primary_key=True)
    title               = Column(String)
    slug                = Column(String)
    date_created        = Column(DateTime)
    latest_date         = Column(DateTime)
    language            = Column(String)
