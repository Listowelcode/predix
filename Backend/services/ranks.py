def get_rank(level):

    ranks = {

        1:"ROOKIE",

        2:"BRONZE",

        3:"SILVER",

        4:"GOLD",

        5:"ELITE"

    }


    return ranks.get(
        level,
        "ROOKIE"
    )