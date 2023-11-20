/*MTD*/

/*Total branches - Market share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @MarketTradingValue DECIMAL(30,2);
SET @MarketTradingValue = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] BETWEEN @FirstDateOfMonth AND @Date
);

WITH

[Branch] AS (
	SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Market Share'
        AND [Year] = YEAR(@Date)
)

, [ValueTotalBranches] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) / @MarketTradingValue / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
	GROUP BY [relationship].[branch_id]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [MarketShare]
		, CASE [MarketShare] 
			WHEN 0 THEN 0
			ELSE [MarketShare] / (SELECT SUM([MarketShare]) FROM [ValueTotalBranches])
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT 
	[Branch].[BranchID]
	, ISNULL([MarketShare], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
    ON [Contribution].[BranchID] = [Branch].[BranchID]


END