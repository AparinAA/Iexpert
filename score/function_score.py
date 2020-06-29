class MyError(BaseException):
    pass


def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def scalar_product_exp_scores(scores):
    mass = [0.3, 0.2, 0.1, 0.2, 0.1]
    result = 0.0
    if len(scores) != 5:
        return 'NO len scores != 5'
    for i in range(5):
        if is_float(str(scores[i])):
            result += mass[i] * scores[i]
        else:
            raise MyError('NO no all scores float')
    return result


def mean_score(scores):
    result = 0.0
    for i in range(5):
        if is_float(str(scores[i])):
            result += scores[i]
        else:
            raise MyError('NO no all scores float')
    return result / len(scores)


def mean_any(scores):
    result = 0.0
    for sc in scores:
        if is_float(str(sc)):
            result += sc
        else:
            raise MyError('NO no all scores float')
    if len(scores) != 0:
        return result / len(scores)
    else:
        raise MyError('zero len')


def scalar_product_com_exp(exp, com):
    try:
        return 0.3 * float(com) + 0.7 * float(exp)
    except:
        raise MyError('NO no all scores float')
