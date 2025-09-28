# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects.mysql import TEXT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class BusiBeam(Base):
    __tablename__ = 'busi_beam'
    __table_args__ = {'comment': '预制梁信息表'}

    id = Column(VARCHAR(64), primary_key=True, default=text("(uuid())"), server_default=text("(uuid())"),
                comment='数据编号')
    code = Column(String(64), comment='预制梁编号')
    qrcode_url = Column(String(255), comment='梁二维码地址')
    parts_name = Column(VARCHAR(255), comment='工程部位')
    source_url = Column(String(255), comment='采集数据包地址')
    beam_type_dic = Column(VARCHAR(64), comment='梁类型（T梁、箱梁、空心梁等）编码')
    beam_height = Column(Integer, comment='梁高度')
    beam_width = Column(Integer, comment='梁宽度')
    beam_length = Column(Integer, comment='梁长度')
    project_id = Column(VARCHAR(64), comment='所属项目ID')
    project_name = Column(VARCHAR(255), comment='项目名称')
    beamfield_id = Column(VARCHAR(64), comment='梁厂id')
    beamfield_name = Column(VARCHAR(255), comment='梁厂名称')
    grade = Column(String(64), comment='评定等级')
    bubble_num = Column(Integer, comment='气泡数量')
    crack_num = Column(Integer, comment='裂缝数量')
    honeycomb_num = Column(Integer, comment='蜂窝数量')
    pittedsurface_num = Column(Integer, comment='麻面数量')
    cornerloss_num = Column(Integer, comment='掉角数量')
    peeling_num = Column(Integer, comment='剥落数量')
    sandlines_num = Column(Integer, comment='砂线数量')
    exposedtendons_num = Column(Integer, comment='露筋数量')
    rootrot_num = Column(Integer, comment='烂根数量')
    holes_num = Column(Integer, comment='孔洞数量')
    remark = Column(TEXT, comment='评价备注')
    report_url = Column(String(255), comment='报告地址')
    create_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                         comment='更新时间')
    check_time = Column(DateTime, comment='检测时间')


class BusiBeamPic(Base):
    __tablename__ = 'busi_beam_pic'
    __table_args__ = {'comment': '预制梁检测信息表'}

    id = Column(VARCHAR(64), primary_key=True, default=text("(uuid())"), server_default=text("(uuid())"),
                comment='数据id')
    beam_code = Column(VARCHAR(64), comment='梁 编码')
    part_type = Column(Integer, comment='部位类型(左侧、右侧）')
    pic_order = Column(Integer, comment='图像顺序')
    pic_length = Column(Integer, comment='图片长度（像素）')
    pic_width = Column(Integer, comment='图片宽度（像素）')
    oripic_url = Column(String(255), comment='原始图片地址')
    markpic_url = Column(String(255), comment='标注图片地址')
    bubble_num = Column(Integer, comment='气泡数量')
    crack_num = Column(Integer, comment='裂缝数量')
    honeycomb_num = Column(Integer, comment='蜂窝数量')
    pittedsurface_num = Column(Integer, comment='麻面数量')
    cornerloss_num = Column(Integer, comment='掉角数量')
    peeling_num = Column(Integer, comment='剥落数量')
    sandlines_num = Column(Integer, comment='砂线数量')
    exposedtendons_num = Column(Integer, comment='露筋数量')
    rootrot_num = Column(Integer, comment='烂根数量')
    holes_num = Column(Integer, comment='孔洞数量')
    status = Column(Integer, comment='状态')
    create_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                         comment='更新时间')

    def __str__(self):
        res = (f'BusiBeamPic: {{beam_code: {self.beam_code}'
               f', par_type: {self.part_type}'
               f', pic_order: {self.pic_order}'
               f', pic_length: {self.pic_length}'
               f', pic_width: {self.pic_width}'
               f', oripic_url: {self.oripic_url}'
               f', markpic_url: {self.markpic_url}'
               f', bubble_num: {self.bubble_num}'
               f', crack_num: {self.crack_num}'
               f', honeycomb_num: {self.honeycomb_num}'
               f', pittedsurface_num: {self.pittedsurface_num}'
               f', cornerloss_num: {self.cornerloss_num}'
               f', peeling_num: {self.peeling_num}'
               f', sandlines_num: {self.sandlines_num}'
               f', exposedtendons_num: {self.exposedtendons_num}'
               f', rootrot_num: {self.rootrot_num}'
               f', holes_num: {self.holes_num}'
               f', status: {self.status}'
               f', create_time: {self.create_time}'
               f', update_time: {self.update_time}'
               f'}}')
        return res

class BusiBeamBuiler:
    def __init__(self):
        self.busi_beam = BusiBeam()
    def code(self, code):
         self.busi_beam.code = code

    def qrcode_url(self,qrcode_rul):
         self.busi_beam.qrcode_url = qrcode_rul

    def parts_name(self, parts_name):
        self.busi_beam.parts_name = parts_name

    def source_url(self, source_url):
        self.busi_beam.source_url = source_url

    def beam_type_dic(self, beam_type_dic):
        self.busi_beam.beam_type_dic = beam_type_dic 

    def beam_height(self, beam_height):
        self.busi_beam.beam_height = beam_height

    def beam_width(self, beam_width):
        self.busi_beam.beam_width = beam_width

    def beam_length(self, beam_length):
        self.busi_beam.beam_length = beam_length

    def project_id(self, project_id):
        self.busi_beam.project_id = project_id

    def project_name(self, project_name):
        self.busi_beam.project_name = project_name

    def beamfield_id(self, beamfield_id):
        self.busi_beam.beamfield_id = beamfield_id

    def beamfield_name(self, beamfield_name):
        self.busi_beam.beamfield_name = beamfield_name
        
    def grade(self, grade):
        self.busi_beam.grade = grade

    def bubble_num(self, bubble_num):
        self.busi_beam.bubble_num = bubble_num

    def crack_num(self, crack_num):
        self.busi_beam.crack_num = crack_num

    def honeycomb_num(self, honeycomb_num):
        self.busi_beam.honeycomb_num = honeycomb_num

    def pittedsurface_num(self, pittedsurface_num):
        self.busi_beam.pittedsurface_num = pittedsurface_num

    def cornerloss_num(self, cornerloss_num):
        self.busi_beam.cornerloss_num = cornerloss_num

    def peeling_num(self, peeling_num):
        self.busi_beam.peeling_num = peeling_num

    def sandlines_num(self, sandlines_num):
        self.busi_beam.sandlines_num = sandlines_num

    def exposedtendons_num(self, exposedtendons_num):
        self.busi_beam.exposedtendons_num = exposedtendons_num

    def rootrot_num(self, rootrot_num):
        self.busi_beam.rootrot_num = rootrot_num

    def holes_num(self, holes_num):
        self.busi_beam.holes_num = holes_num

    def remark(self, remark):
        self.busi_beam.remark = remark

    def report_url(self, report_url):
        self.busi_beam.report_url = report_url

    def create_time(self, create_time):
        self.busi_beam.create_time = create_time

    def update_time(self, update_time):
        self.busi_beam.update_time = update_time

    def check_time(self, check_time):
        self.busi_beam.check_time = check_time

class BusiBeamPicBuiler:
    def __init__(self):
        self.busi_beam_pic = BusiBeamPic()

    def beam_code(self, beam_code: str):
        self.busi_beam_pic.beam_code = beam_code
        return self

    def part_type(self, part_type: str):
        self.busi_beam_pic.part_type = part_type
        return self

    def pic_order(self, pic_order: str):
        self.busi_beam_pic.pic_order = pic_order
        return self

    def pic_length(self, pic_length: str):
        self.busi_beam_pic.pic_length = pic_length
        return self

    def pic_width(self, pic_width: int):
        self.busi_beam_pic.pic_width = pic_width
        return self

    def oripic_url(self, oripic_url: str):
        self.busi_beam_pic.oripic_url = oripic_url
        return self

    def markpic_url(self, markpic_url: str):
        self.busi_beam_pic.markpic_url = markpic_url
        return self

    def bubble_num(self, bubble_num: int):
        self.busi_beam_pic.bubble_num = bubble_num
        return self

    def crack_num(self, crack_num: int):
        self.busi_beam_pic.crack_num = crack_num
        return self

    def honeycomb_num(self, honeycomb_num: int):
        self.busi_beam_pic.honeycomb_num = honeycomb_num
        return self

    def pittedsurface_num(self, pittedsurface_num: int):
        self.busi_beam_pic.pittedsurface_num = pittedsurface_num
        return self

    def cornerloss_num(self, cornerloss_num: int):
        self.busi_beam_pic.cornerloss_num = cornerloss_num
        return self

    def peeling_num(self, peeling_num: int):
        self.busi_beam_pic.peeling_num = peeling_num
        return self

    def sandlines_num(self, sandlines_num: int):
        self.busi_beam_pic.sandlines_num = sandlines_num
        return self

    def exposedtendons_num(self, exposedtendons_num: int):
        self.busi_beam_pic.exposedtendons_num = exposedtendons_num
        return self

    def rootrot_num(self, rootrot_num: int):
        self.busi_beam_pic.rootrot_num = rootrot_num
        return self

    def holes_num(self, holes_num: int):
        self.busi_beam_pic.holes_num = holes_num
        return self

    def status(self, status: int):
        self.busi_beam_pic.status = status
        return self

    def build(self):
        return self.busi_beam_pic
