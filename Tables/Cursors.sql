DELIMITER //
CREATE PROCEDURE CalculateTotalInvestment()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE buyerId INT;
    DECLARE totalInvestment DECIMAL(15,2);
    DECLARE buyerCursor CURSOR FOR 
    SELECT BuyerId FROM Buyer;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN buyerCursor;

    read_loop: LOOP
        FETCH buyerCursor INTO buyerId;
        IF done THEN
            LEAVE read_loop;
        END IF;
        SELECT SUM(Quantity * PurchasePrice) INTO totalInvestment
        FROM Portfolio
        WHERE BuyerId = buyerId;
        IF totalInvestment IS NULL THEN
            SET totalInvestment = 0;
        END IF;

        UPDATE Buyer 
        SET Capital = totalInvestment 
        WHERE BuyerId = buyerId;
    END LOOP;

    CLOSE buyerCursor;
END //
DELIMITER ;

DELIMITER //

CREATE PROCEDURE DistributeDividends()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE buyerId INT;
    DECLARE totalHolding DECIMAL(15,2);
    DECLARE dividendAmount DECIMAL(10,2);
    DECLARE buyerCursor CURSOR FOR 
    SELECT DISTINCT BuyerId FROM Portfolio;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    OPEN buyerCursor;
    read_loop: LOOP
        FETCH buyerCursor INTO buyerId;
        IF done THEN
            LEAVE read_loop;
        END IF;
        SELECT SUM(Quantity * PurchasePrice) INTO totalHolding
        FROM Portfolio
        WHERE BuyerId = buyerId;
        IF totalHolding IS NULL THEN
            SET totalHolding = 0;
        END IF;
        SET dividendAmount = totalHolding * 0.02;
        INSERT INTO Dividend (BuyerId, Date, Amount) 
        VALUES (buyerId, CURDATE(), dividendAmount);
    END LOOP;

    CLOSE buyerCursor;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE ApplyCommissionToStockPrices()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE stockId INT;
    DECLARE platformId INT;
    DECLARE stockPrice DECIMAL(10,2);
    DECLARE commissionRate DECIMAL(5,2);
    DECLARE stockCursor CURSOR FOR 
    SELECT StockId, PlatformId FROM Updates;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    OPEN stockCursor;
    read_loop: LOOP
        FETCH stockCursor INTO stockId, platformId;
        IF done THEN
            LEAVE read_loop;
        END IF;
        SELECT Commission INTO commissionRate 
        FROM BrokerPlatform 
        WHERE PlatformId = platformId;
        SELECT Price INTO stockPrice 
        FROM Stocks 
        WHERE StockId = stockId;
        UPDATE Stocks
        SET Price = stockPrice * (1 + commissionRate / 100)
        WHERE StockId = stockId;
    END LOOP;

    CLOSE stockCursor;
END //

DELIMITER ;
