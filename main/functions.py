def get_periodo_actual():
    """
    get_periodo_actual Devuelve el periodo actual en formato AAAAMM
    """
    from time import gmtime, strftime
    return strftime("%Y%m", gmtime())


def range_month(date1, date2):
    date_aux = str(date1)
    context = []
    context.append(int(date_aux))
    while int(date_aux) < int(date2):
        if int(date_aux[4:]) < 12:
            date_aux = str(date_aux)[:4] + str(int(str(date_aux)[4:]) + 1).zfill(2)
        else:
            date_aux = str(int(str(date_aux)[:4]) + 1) + '01'
        context.append(int(date_aux))
    return sorted(context)
