import logging  # 引入logging模块
import logging.handlers
import os.path
import time


def logger_init():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级总开关
    # 第二步，创建一个handler，用于写入日志文件
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))

    log_path = os.path.join(os.getcwd(), 'Logs')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = os.path.join(log_path, rq + 'Measures.log')

    fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=1024, backupCount=5)

    # fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    st = logging.StreamHandler()
    st.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 第三步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

    fh.setFormatter(formatter)
    st.setFormatter(formatter)

    # 第四步，将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(st)
    return logger
