import configparser
import os


class ReadConfig:
    def __init__(self, file_name):
        pro_dir = os.path.split(os.path.realpath(__file__))[0]
        self.config_path = os.path.join(pro_dir, file_name)
        self.conf = configparser.ConfigParser()
        self.conf.read(self.config_path)

    def get_config(self, section, option):
        """
        :param section: 服务
        :param option: 配置参数
        :return:返回配置信息
        """
        config = self.conf.get(section, option)
        return config

    def update_config(self, section, option, content):
        self.conf.remove_option(section, option)
        self.conf.set(section, option, content)
        with open(self.config_path, 'w') as f:
            self.conf.write(f)
        pass


if __name__ == "__main__":
    read_config = ReadConfig("config.ini")
    print(read_config.get_config("database", "file_path"))
