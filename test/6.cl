class Main {
    b: AUTO_TYPE;
    c: AUTO_TYPE;

    function(a: AUTO_TYPE, d: AUTO_TYPE): AUTO_TYPE {
        {
            b <- a;
            d <- b;
            c <- d;
            factorial(a);
        }
    };

    factorial(n: AUTO_TYPE): AUTO_TYPE {
        if n = 1 then 1 else n * factorial(n - 1) fi
    };
};