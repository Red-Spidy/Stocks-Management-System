use stock_management;
DELIMITER //
CREATE TRIGGER UpdateStockPriceAfterTransaction
AFTER INSERT ON Information
FOR EACH ROW
BEGIN
    DECLARE newPrice DECIMAL(10,2);
    SELECT Price INTO newPrice
    FROM Stocks
    WHERE StockId = NEW.StockId;
    UPDATE Stocks
    SET Price = newPrice * 1.05
    WHERE StockId = NEW.StockId;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER UpdateProfitLossAfterPurchase
AFTER INSERT ON Portfolio
FOR EACH ROW
BEGIN
    DECLARE totalInvestment DECIMAL(15,2);
    SELECT SUM(Quantity * PurchasePrice) INTO totalInvestment
    FROM Portfolio
    WHERE BuyerId = NEW.BuyerId;
    UPDATE Buyer
    SET ProfitLoss = totalInvestment - Buyer.Capital
    WHERE BuyerId = NEW.BuyerId;
END //
DELIMITER ;
DELIMITER //

CREATE TRIGGER DeleteAssociatedDataOnStockDeletion
AFTER DELETE ON Stocks
FOR EACH ROW
BEGIN
    DELETE FROM Portfolio
    WHERE StockId = OLD.StockId;
    DELETE FROM Buys
    WHERE StockId = OLD.StockId;
    DELETE FROM Information
    WHERE StockId = OLD.StockId;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER UpdateProfitLossAfterDividend
AFTER INSERT ON Dividend
FOR EACH ROW
BEGIN
    DECLARE currentProfitLoss DECIMAL(15,2);
    SELECT ProfitLoss INTO currentProfitLoss
    FROM Buyer
    WHERE BuyerId = NEW.BuyerId;
    UPDATE Buyer
    SET ProfitLoss = currentProfitLoss + NEW.Amount
    WHERE BuyerId = NEW.BuyerId;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER UpdateStockPriceOnBrokerChange
AFTER UPDATE ON Updates
FOR EACH ROW
BEGIN
    DECLARE commissionRate DECIMAL(5,2);
    DECLARE newPrice DECIMAL(10,2);
    SELECT Commission INTO commissionRate
    FROM BrokerPlatform
    WHERE PlatformId = NEW.PlatformId;
    SELECT Price INTO newPrice
    FROM Stocks
    WHERE StockId = NEW.StockId;
    UPDATE Stocks
    SET Price = newPrice * (1 + commissionRate / 100)
    WHERE StockId = NEW.StockId;
END //

DELIMITER ;

DELIMITER //
CREATE TRIGGER UpdateKYCStatusAfterPurchase
AFTER INSERT ON Portfolio
FOR EACH ROW
BEGIN
    DECLARE kycStatus VARCHAR(20);
    IF (SELECT COUNT(*) FROM Portfolio WHERE BuyerId = NEW.BuyerId) > 5 THEN
        SET kycStatus = 'Verified';
    ELSE
        SET kycStatus = 'Pending';
    END IF;
    UPDATE Buyer
    SET KYCStatus = kycStatus
    WHERE BuyerId = NEW.BuyerId;
END //
DELIMITER ;
DELIMITER //
CREATE TRIGGER after_buy_insert
AFTER INSERT ON Buys
FOR EACH ROW
BEGIN
		INSERT INTO Portfolio (BuyerId, StockId, StockName, Quantity, PurchasePrice)
		SELECT NEW.BuyerId, Stocks.StockId, Stocks.StockName, 1, Stocks.Price
		FROM Stocks
		WHERE Stocks.StockId = NEW.StockId;
END//
DELIMITER ;

