xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]


xpath_str = """.//*[not(contains(@style, 'display: none'))and not(contains(@style, 'display:none'))and not(contains(@class, 'port'))]/text()

                                """



