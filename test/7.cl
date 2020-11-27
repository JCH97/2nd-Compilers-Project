class Main inherits IO {

    b: AUTO_TYPE <- c;
    c: AUTO_TYPE <- b;

    f(a: AUTO_TYPE): AUTO_TYPE{
        if a < 3 then 1 else f(a - 1) + f(a - 2) fi
    };
};