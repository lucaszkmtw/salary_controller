function monthDiff(d1, d2) {
    var months;
    months = (d2.getFullYear() - d1.getFullYear()) * 12;
    months -= d1.getMonth() + 1;
    months += d2.getMonth();
    return months <= 0 ? 0 : months;
}

monthDiff(
    new Date(2008, 10, 4), // November 4th, 2008
    new Date(2010, 2, 12)  // March 12th, 2010
);
// Result: 15: December 2008, all of 2009, and Jan & Feb 2010

monthDiff(
    new Date(2010, 0, 1),  // January 1st, 2010
    new Date(2010, 2, 12)  // March 12th, 2010
);
// Result: 1: February 2010 is the only full month between them

monthDiff(
    new Date(2010, 1, 1),  // February 1st, 2010
    new Date(2010, 2, 12)  // March 12th, 2010
);
// Result: 0: There are no *full* months between them