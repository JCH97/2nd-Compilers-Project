class Point {
    a: AUTO_TYPE;
    b: AUTO_TYPE;

    init(x: AUTO_TYPE, y: AUTO_TYPE): AUTO_TYPE {{
        a <- b;
        b <- x + y;
        create_point();
    }};

    create_point(): AUTO_TYPE { new Point };
};