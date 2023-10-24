# -*- coding: utf-8 -*-

BOT_NAME = 'scraps'

SPIDER_MODULES = ['scraps.spiders']
NEWSPIDER_MODULE = 'scraps.spiders'

LOG_LEVEL = 'INFO'
LOG_FILE = 'output.log'

ROBOTSTXT_OBEY = True

SAVE_CONTENT = 'scraps.jl'
ITEM_PIPELINES = {
    'scraps.pipelines.ChanelPipeline': 300,
}
