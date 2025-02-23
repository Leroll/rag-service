import logging
import os
import datetime
import time
import fcntl
from logging.handlers import TimedRotatingFileHandler

class MultiCompatibleTimedRotatingFileHandler(TimedRotatingFileHandler):
    def computeRollover(self, currentTime: int) -> int:
        # 改写函数，将时间取整
        t_str = time.strftime(self.suffix, time.localtime(currentTime))
        t = time.mktime(time.strptime(t_str, self.suffix))
        return super().computeRollover(t)
    
    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        #-- 兼容多进程并发  begin --# 
        if not os.path.exists(dfn):
            try:
                self.rotate(self.baseFilename, dfn)
            except FileNotFoundError:
                # 这里出现 未找到日志文件的异常，则说明已经有其他进程对日志文件重命名了，忽略即可，当前日志不会丢失
                pass
        #-- 兼容多进程并发 end --#
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour 
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


class LoggerGenerator():
    def __init__(self, log_path, logger_name, log_level=logging.INFO):
        abs_log_path = os.path.abspath(log_path)
        log_dir_path = os.path.dirname(abs_log_path)
        if os.path.exists(log_dir_path) == False:
            os.makedirs(log_dir_path)
            
        formatter = logging.Formatter(fmt='%(asctime)s,%(msecs)03d [%(levelname)s] : %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        
        at_time = datetime.datetime.strptime('04:02', '%H:%M')
        handler = MultiCompatibleTimedRotatingFileHandler(abs_log_path, when='midnight', atTime=at_time, interval=1, backupCount=0)
        # handler = logging.FileHandler(abs_log_path, mode='a')
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.addHandler(handler)
        
        self._logger = logger
        
    def get_logger(self):
        return self._logger
    
    
class ActivateIDFilter(logging.Filter):
    """过滤用于保持进程激活的ID
    """
    def filter(self, record):
        if 'activate_session_001' in record.msg:
            return False
        else:
            return True
        
if __name__ == '__main__':
    test_log = LoggerGenerator('./logs/test.log', 'test_logger').get_logger()
    test_log.debug('debug_message')
    test_log.info('info_message')
    test_log.error('error_message')
    test_log.critical('critical_message')
        