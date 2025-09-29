from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# 数据库模型导入
from db.dbModels import *
import time
import yaml
import logging


database_yaml = 'config/database.yaml'
with open(file=database_yaml, mode='r', encoding='utf-8') as f:
    database_config = f.read()
    yaml_data = yaml.load(stream=database_config, Loader=yaml.FullLoader)
url = yaml_data['mysql']
user = yaml_data['user']
password = yaml_data['password']
database = yaml_data['database']
database_open = yaml_data['database_open']

mysql_url = f"mysql+pymysql://{user}:{password}@{url}/{database}?charset=utf8"
logging.info(f'mysql连接信息：{mysql_url}')
# 创建数据库连接
# engine = create_engine(f"mysql+pymysql://root:root123456@192.168.105.58:3306/ruoyi?charset=utf8")
engine = create_engine(mysql_url)
Session = sessionmaker(bind=engine)
session = Session()


def update_busi_beam_pic(data: BusiBeamPic):
    # 外观检测图像结果信息
    # beamPic = BusiBeamPic()
    # beamPic.beam_code = "A-001"
    # beamPic.bubble_num = 10
    # beamPic.part_type = 1
    # 保存数据
    session.add(data)
    session.commit()
    logging.debug(data.id)

def update_busi_beam_pic_list(data: list):
    # 外观检测图像结果信息
    # beamPic = BusiBeamPic()
    # beamPic.beam_code = "A-001"
    # beamPic.bubble_num = 10
    # beamPic.part_type = 1
    # 保存数据
    session.add_all(data)
    # session.commit()
    logging.debug(data.id)


def update_busi_beam(beam_code: str, defects: dict):
    # 梁外观检测结果信息
    # beam = BusiBeam()
    # beam.code = "A-003"
    # beam.bubble_num = 10
    # beam.part_type = 1
    # 保存数据
    # session.add(data)
    grade = 'A'
    remark =  '''
缺陷原因及改进建议:''' if (defects['bubble_num'] + defects['crack_num']) > 0 else ''
    bubble_remark = '气泡：脱模剂的种类选用不当，或脱模剂的使用方法不正确（包括模板清理、涂刷方式、涂刷厚度）；浇筑厚度未准确量测，仅凭借经验或是感觉确定混凝土浇筑高度，易导致分层厚度过大；骨料级配不合理，粗骨料多，细骨料少，混凝土浆体不足，排气不畅；外加剂：在满足设计要求时，尽量降低含气量；消泡剂能大大减少搅拌和浇筑引起的气泡，保水剂能降低黏度，使气泡易排出。水泥和掺合料：水泥用量不足、用水量和自由水数量较多，水化后会残留气泡。建议加强振捣工艺，标准化施工，尽可能地排除混凝土内部、外部的水泡；优化配合比，可以考虑添加引气剂，以提高混凝土气体的排除；选用级配良好的粗、细集料，在保证强度的前提下，尽可能的提升混凝土砂率的波动范围。'
    crack_remark = '裂缝：养护不当导致的裂缝：混凝土与空气接触面积较大时，如养护不当或养护不及时则容易失水，从而使混凝土出现裂缝；温度应力产生裂缝：混凝土水化初期内表温差较大时，在温度应力作用下易产生裂缝。建议浇筑完成后，待混凝土外表温度与自然温度相差不超过15℃时，立即进行养护，养护周期不少于7d，面板需覆盖养护，避免暴晒；振捣密实而不离析，对面板进行二次抹压，以减少收缩量。'
    if defects['bubble_num'] > 0:
        remark = remark + f'\n{bubble_remark}'
    if defects['crack_num'] > 0:
        remark = remark + f'\n{crack_remark}'

    stmt = f'''UPDATE busi_beam SET bubble_num = :bubble_num
    , crack_num = :crack_num
    , honeycomb_num = :honeycomb_num
    , pittedsurface_num = :pittedsurface_num
    , cornerloss_num = :cornerloss_num
    , peeling_num = :peeling_num
    , sandlines_num = :sandlines_num
    , exposedtendons_num = :exposedtendons_num
    , rootrot_num = :rootrot_num
    , holes_num = :holes_num
    , grade = :grade
    , remark = :remark
    , check_time = :check_time
    WHERE code  = :code'''

    values = {
            'bubble_num': defects['bubble_num'],
            'crack_num': defects['crack_num'],
            'honeycomb_num': defects['honeycomb_num'],
            'pittedsurface_num': defects['pittedsurface_num'],
            'cornerloss_num': defects['cornerloss_num'],
            'peeling_num': defects['peeling_num'],
            'sandlines_num': defects['sandlines_num'],
            'exposedtendons_num': defects['exposedtendons_num'],
            'rootrot_num': defects['rootrot_num'],
            'holes_num': defects['holes_num'],
            'grade': grade,
            'remark': remark,
            'check_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'code': beam_code
        }

    with engine.begin() as conn:
        logging.debug(f'sql: {stmt}, values: {values}')
        conn.execute(text(stmt), values)