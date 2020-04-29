from formparser import FormParser


def _parse_form(response: any) -> bool:
    form_parser = FormParser()
    parser = form_parser
    try:
        parser.feed(str(response.content))
    except:
        return False

    return True
