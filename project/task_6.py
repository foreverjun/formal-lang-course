from pyformlang.cfg import CFG


def cfg_to_weak_cnf(cfg: CFG) -> CFG:
    """
    Transforms CFG to weak CNF
    :param cfg: The CFG to transform
    :return: The weak CNF, equivalent to the CFG
    """
    # remove useless symbols and chain productions
    buf_cfg = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )
    # remove "pairs" of terminal
    res_prod = buf_cfg._get_productions_with_only_single_terminals()
    #
    res_prod = buf_cfg._decompose_productions(res_prod)
    return CFG(start_symbol=buf_cfg.start_symbol, productions=set(res_prod))


def cfg_from_file(file_name: str, start_symbol: str = "S") -> CFG:
    """
    Reads CFG from file
    :param start_symbol: Start symbol of the CFG
    :param file_name: The file name
    :return: The CFG
    """
    with open(file_name, "r") as file:
        return CFG.from_text(file.read(), start_symbol=start_symbol)


def cfg_to_file(cfg: CFG, file_name: str):
    """
    Writes CFG to file
    :param cfg: The CFG
    :param file_name: The file name
    """
    with open(file_name, "w") as file:
        file.write(cfg.to_text())
