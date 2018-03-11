# -*- coding: ShiftJIS -*-
import sys
import os
import math

# �g����
if len(sys.argv) == 1:
    print("")
    print("Fran.exe �� LidarGen5.exe �ŕۑ����� LiDAR �̋����f�[�^(csv �t�@�C���j")
    print("��ǂݍ���ŁAx y z �� 3 �����_�Q���W�l���o��")
    print("���������� x �A���������� z�A���s�������� y")
    print("")
    print("[Usage] %s depth.csv [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-frame frame_index: �w�肵���t���[���̂ݏo�́B0 �n�܂�̔ԍ�")
    print("-out_dir dir_name: �o�̓t�H���_�̎w��B������΍��B�f�t�H���g�� out")
    print("-xrange x_min x_max: x_min < x < x_max �ȓ_�����o��")
    print("-yrange y_min y_max: ��Ɠ��l")
    print("-zrange z_min z_max: ��Ɠ��l")
    print("")
    exit(0)

# -------------------------------------------------------------------------------------
# �ݒ�
# -------------------------------------------------------------------------------------

# �S�t���[���o�͎��̏o�̓f�B���N�g��
OUT_DIR = "out"

# �S�t���[���o�͎��̃t�@�C��������
OUT_FILE = "%04d.txt"

# -------------------------------------------------------------------------------------
# �֐�
# -------------------------------------------------------------------------------------

# �w�肵�������񂪈������X�g�̒��ɂ��邩�`�F�b�N
def foundOpt( argv, opt, idx = []):
    if opt in argv:
        if len(idx) > 0:
            idx[0] = argv.index(opt)
        else:
            idx.append(argv.index(opt))
        return True
    else:
        return False

# �J���}��؂�� 1 �s�̋����f�[�^���O�����_�Q���W�l�ɓW�J
#�E3�������W�l�̃��X�g��Ԃ�
#�E�^����ꂽ�����񂪖����ȃt�H�[�}�b�g�ł���΋�̃��X�g��Ԃ�
def expandTo3d( 
    line_str, # �J���}��؂�� 1 �s�̋����f�[�^
    sensor_h_cols = 141, # �Z���T�[�̐�����f��
    sensor_h_angle_start = -70.0, # �Z���T�[�̈�ԍ��̗�̕��ʊp [deg]
    sensor_h_angle_step = 1.0, # �Z���T�[�̐�������\ [deg]
    sensor_v_lines = ( # �Z���T�[�̃��C�����̐�������\
        1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 
        0.6, 0.6, 
        0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 
        1.2, 1.2, 1.2, 1.2
    ), 
    sensor_v_angle_start = 9.4, # �Z���T�[�̈�ԏ�̃��C���̋p [deg]
    big_dist_val = 16000, # �����l�ُ̈�l�F���̒l���傫�Ȓl�� 0 �ɂ���
    x_range_min = None, # x ���W�l�����̒l��菬�����_�͏o�͂��Ȃ�
    x_range_max = None, # x ���W�l�����̒l���傫���_�͏o�͂��Ȃ�
    y_range_min = None, # y ���W�l�����̒l��菬�����_�͏o�͂��Ȃ�
    y_range_max = None, # y ���W�l�����̒l���傫���_�͏o�͂��Ȃ�
    z_range_min = None, # z ���W�l�����̒l��菬�����_�͏o�͂��Ȃ�
    z_range_max = None, # z ���W�l�����̒l���傫���_�͏o�͂��Ȃ�
     ):

    # �Ԃ�l
    pointList = []

    # ������f��
    width = sensor_h_cols

    # ������f��
    height = len(sensor_v_lines)

    # csv �t�@�C���̗�
    num_cols = width * height + 1

    # �J���}�ŗ񕪊�
    la = line_str.split(',')

    # �񐔂�����̐���������
    if len(la) == num_cols:

        # �������ʊp [deg]
        pitch_deg = 0.0

        # �f�[�^�ǂݍ���
        for i in range(height):
            for j in range(width):

                # �����l
                try:
                    dist = float(la[i * width + j + 1]) # �ŏ��̗�͔�΂�
                except:
                    # ���s�����炻���ŏI��
                    return []

                # �ُ�l�� 0 �ɂ���
                if dist > big_dist_val:
                   dist = 0

                # �������ʊp
                yaw_rad = (sensor_h_angle_start + sensor_h_angle_step * j) * math.pi / 180.0 

                # x ���W�l
                x = dist * math.sin(yaw_rad)

                # y ���W�l
                y = dist * math.cos(yaw_rad)

                # �������ʊp [rad]
                pitch_rad = (sensor_v_angle_start - pitch_deg) * math.pi / 180.0

                # z ���W�l
                z = dist * math.sin(pitch_rad)

                # �͈͊O�`�F�b�N
                if (x_range_min != None and x < x_range_min) or \
                    (x_range_max != None and x > x_range_max) or \
                    (y_range_min != None and y < y_range_min) or \
                    (y_range_max != None and y > y_range_max) or \
                    (z_range_min != None and z < z_range_min) or \
                    (z_range_max != None and z > z_range_max):
                    continue

                #���X�g�ǉ�
                pointList.append([x, y, z])

            # �������ʊp�̃C���N�������g
            pitch_deg += sensor_v_lines[i]

    return pointList

# �_�Q�f�[�^�̏o��
def writePointList( 
    point_list, # 3�������W�l�̃��X�g
    stream = sys.stdout # �o�͐�
    ):
    for a in point_list:
        out_str = "%f %f %f \n" % (a[0], a[1], a[2])
        stream.write(out_str)

# -------------------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------------------

# ���̓t�@�C����
input_file_name = sys.argv[1]

# �t���[���ԍ��w��
single_frame = False
frame_to_read = 0
i = []
if foundOpt(sys.argv, "-frame", i):
    single_frame = True
    frame_to_read = int(sys.argv[i[0] + 1])

# �o�̓f�B���N�g��
out_dir = OUT_DIR
if foundOpt(sys.argv, "-out_dir", i):
    out_dir = sys.argv[i[0] + 1]

# �f�B���N�g���A������������
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

# �͈͎w��
x_min = None
x_max = None
if foundOpt(sys.argv, "-xrange", i):
    x_min = float(sys.argv[i[0] + 1])
    x_max = float(sys.argv[i[0] + 2])
y_min = None
y_max = None
if foundOpt(sys.argv, "-yrange", i):
    y_min = float(sys.argv[i[0] + 1])
    y_max = float(sys.argv[i[0] + 2])
z_min = None
z_max = None
if foundOpt(sys.argv, "-zrange", i):
    z_min = float(sys.argv[i[0] + 1])
    z_max = float(sys.argv[i[0] + 2])

# �t���[���J�E���^�[
frame_count = 0

# ���̓t�@�C�����P�s���ǂݍ���
for line in open(input_file_name):
    
    # 3�����W�J
    pointList = expandTo3d(line,
    x_range_min=x_min, x_range_max=x_max,
    y_range_min=y_min, y_range_max=y_max,
    z_range_min=z_min, z_range_max=z_max,
    )

    # ����������
    if len(pointList) > 0:

        # �P�t���[���\���̏ꍇ
        if single_frame:
            
            # ����̃t���[���ԍ��ɒB������
            if frame_count == frame_to_read:

                # ��ʂɏo��
                writePointList(pointList)

                # �I��
                break

        # �S�t���[���o�͂̏ꍇ
        else:

            # �o�̓t�@�C����
            out_filename = OUT_FILE % frame_count

            # �o�̓t�@�C�����t���p�X
            out_filepath = "%s/%s" % (out_dir, out_filename)

            # �t�@�C�����J��
            try:
                outf = open(out_filepath, "w")
            except:
                print("ERROR: Failed to open the file, " + out_filepath)
                exit(-1)

            # ��������
            writePointList(pointList, outf)

            # �t�@�C�������
            outf.close()

            # gnuplot �p�o��
            print("splot '%s' w p" % out_filename)
            print("pause -1")

        # �t���[�����̃J�E���g
        frame_count += 1

# EOP
exit(0)

