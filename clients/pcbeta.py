from libs.discuz import Discuz


class PcBeta(Discuz):

    def __init__(self):
        super(PcBeta, self).__init__()
        self.base_url = 'http://bbs.pcbeta.com'
        self.charset = 'gbk'

    def _handler(self, username, password, **kwargs):
        data = self.login2(username, password)
        self.logger.info(data['message'])
        html = self.fetch('http://i.pcbeta.com/home.php?mod=task&do=apply&id=149').text
        if html.find('恭喜您，任务已成功完成') != -1:
            self.logger.info('恭喜您，任务已成功完成，您将收到奖励通知，请注意查收')
            return
        if html.find('本期您已申请过此任务') != -1:
            self.logger.warning('抱歉，本期您已申请过此任务，请下期再来')
            return
        self.logger.warning('签到异常')
