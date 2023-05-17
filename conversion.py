import json

from xml.etree.ElementTree import Element, parse

import urllib3


class Charles:
    def __init__(self, file):
        self.file = file
        with open(file, encoding='utf-8') as f:
            self.data = json.load(f)

    @property
    def requests(self):
        return [HttpRequest(**data.get('request')) for data in self.data.get('log').get('entries')]

    def jmeter(self, file):
        jmeter = parse('template.jmx')
        root = jmeter.getroot()
        element = root.find(".//hashTree/hashTree/hashTree")
        for request in self.requests:
            element.append(request.get_jmeter_xml())
        jmeter.write(file, encoding='utf-8')
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read().replace("</HTTPSamplerProxy>", "</HTTPSamplerProxy></hashTree>")
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)


class HttpRequest:
    def __init__(self, method, url, cookies, headers, postData=None, queryString=None, **kwargs):
        self.method = method
        self.url = url
        self.cookies = cookies
        self.headers = headers
        self.queryString = queryString
        self.postData = postData

    @property
    def protocol(self):
        return urllib3.get_host(self.url)[0]

    @property
    def port(self):
        port = urllib3.get_host(self.url)[2]
        if not port:
            port = "443" if 'https' == self.protocol else "80"
        return port

    @property
    def path(self):
        start_index = self.url.find(self.hostname) + len(self.hostname)
        end_index = self.url.find("?")
        if end_index == -1:
            return self.url[start_index:]
        else:
            return self.url[start_index:end_index]

    @property
    def hostname(self):
        return urllib3.get_host(self.url)[1]

    def get_jmeter_xml(self):
        def append_sub_element(parent, sub_tag, text, **kwargs):
            sub_element = Element(sub_tag, **kwargs)
            if text:
                sub_element.text = text
            parent.append(sub_element)

        sampler = Element('HTTPSamplerProxy', guiclass='HttpTestSampleGui', testclass='HTTPSamplerProxy',
                          testname=f"{self.method} {self.path}")
        if self.postData:
            post_body = Element('boolProp', name='HTTPSampler.postBodyRaw')
            post_body.text = 'true'
            sampler.append(post_body)
            arguments = Element('elementProp', name="HTTPsampler.Arguments", elementType="Arguments")
            collection = Element('collectionProp', name="Arguments.arguments")
            element = Element('elementProp', name="", elementType="HTTPArgument")
            append_sub_element(element, 'boolProp', "false", name="HTTPArgument.always_encode")
            text = json.dumps(json.loads(self.postData.get('text')), ensure_ascii=False, indent=4)
            append_sub_element(element, 'stringProp', text, name="Argument.value")
            append_sub_element(element, 'stringProp', '=', name="Argument.metadata")
            collection.append(element)
            arguments.append(collection)
            sampler.append(arguments)
        if self.queryString:
            query = Element('elementProp', name="HTTPsampler.Arguments", elementType="Arguments",
                            guiclass="HTTPArgumentsPanel", testclass="Arguments", testname="用户定义的变量", enabled="true")
            collection = Element('collectionProp', name="Arguments.arguments")
            for element in self.queryString:
                _e = Element('elementProp', name=element.get('name'), elementType="HTTPArgument")
                _es1 = Element('boolProp', name='HTTPArgument.always_encode')
                _es1.text = "false"
                _e.append(_es1)
                _es2 = Element('stringProp', name='Argument.value')
                _es2.text = element.get('value')
                _e.append(_es2)
                _es3 = Element('stringProp', name='Argument.metadata')
                _es3.text = "="
                _e.append(_es3)
                _es4 = Element('boolProp', name='HTTPArgument.use_equals')
                _es4.text = "true"
                _e.append(_es4)
                _es5 = Element('stringProp', name='Argument.name')
                _es5.text = element.get('name')
                _e.append(_es5)
                collection.append(_e)
            query.append(collection)
            sampler.append(query)
        append_sub_element(sampler, 'stringProp', self.hostname, name="HTTPSampler.domain")
        append_sub_element(sampler, 'stringProp', self.port, name="HTTPSampler.port")
        append_sub_element(sampler, 'stringProp', self.protocol, name="HTTPSampler.protocol")
        append_sub_element(sampler, 'stringProp', 'utf-8', name="HTTPSampler.contentEncoding")
        append_sub_element(sampler, 'stringProp', self.path, name="HTTPSampler.path")
        append_sub_element(sampler, 'stringProp', self.method.upper(), name="HTTPSampler.method")
        append_sub_element(sampler, 'boolProp', "true", name="HTTPSampler.follow_redirects")
        append_sub_element(sampler, 'boolProp', "false", name="HTTPSampler.auto_redirects")
        append_sub_element(sampler, 'boolProp', "true", name="HTTPSampler.use_keepalive")
        append_sub_element(sampler, 'boolProp', "false", name="HTTPSampler.DO_MULTIPART_POST")
        append_sub_element(sampler, 'stringProp', "", name="HTTPSampler.embedded_url_re")
        append_sub_element(sampler, 'stringProp', "", name="HTTPSampler.connect_timeout")
        append_sub_element(sampler, 'stringProp', "", name="HTTPSampler.response_timeout")
        return sampler


if __name__ == '__main__':
    Charles("charles.har").jmeter("jmeter.jmx")
