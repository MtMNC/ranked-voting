class Vote:
    """
    A Vote contributes its value (a positive number <= Vote.MAX_VALUE) to an Entry's total value.
    The Vote's value may be rescaled once to be smaller so that its Voter can distribute some of
    their support to another Entry.
    """


    # the maximum value a Vote can have;
    # also, the maximum value that each Voter can split across all of their Votes
    MAX_VALUE = 1


    def __init__(self, voter, rank, original_value, round_when_first_cast):
        assert original_value > 0 and original_value <= Vote.MAX_VALUE

        self.voter = voter
        self.rank = rank
        self.original_value = original_value
        self.value = original_value
        self.round_when_first_cast = round_when_first_cast
        self.has_rescaled = False


    def rescale(self, rescale_factor, round_when_rescaled):
        """
        Rescale the Vote's value by the given multiplicative factor and record the round when this
        rescaling took place.
        """

        assert rescale_factor > 0 and rescale_factor < 1
        assert not self.has_rescaled, "A Vote can only be rescaled once"

        self.rescale_factor = rescale_factor
        self.value *= rescale_factor
        self.has_rescaled = True
        self.round_when_rescaled = round_when_rescaled


    def __str__(self):
        text = f"+{self.value} from {self.voter.name} assigning rank {self.rank}"
        text += f"\n\t* cast with value {self.original_value} in round {self.round_when_first_cast}"
        if self.has_rescaled:
            text += f"\n\t* rescaled by factor {self.rescale_factor} in round {self.round_when_rescaled}"

        return text