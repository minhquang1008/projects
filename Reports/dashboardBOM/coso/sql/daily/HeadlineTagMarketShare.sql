/*Daily*/

/*Headline Tag - Market Share (Phần trăm hoàn thành chỉ tiêu ngày - Thị phần) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

DECLARE @PrevMarketTradingValue DECIMAL(30,2);
SET @PrevMarketTradingValue = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] = @Prev
);

DECLARE @TodayMarketTradingValue DECIMAL(30,2);
SET @TodayMarketTradingValue = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] = @Date
);

WITH

[BranchTarget] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [PrevMarketShareByBranch] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) / @PrevMarketTradingValue / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Prev
	GROUP BY [relationship].[branch_id]
)

, [TodayMarketShareByBranch] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[value]) / @TodayMarketTradingValue / 2 [MarketShare]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
	GROUP BY [relationship].[branch_id]
)

, [result] AS (
	SELECT
		[BranchTarget].[BranchID]
		, ISNULL([TodayMarketShareByBranch].[MarketShare],0) [MarketShare]
		, ISNULL([TodayMarketShareByBranch].[MarketShare],0) - ISNULL([PrevMarketShareByBranch].[MarketShare],0) [AbsoluteChange]
		, CASE 
			WHEN ISNULL([PrevMarketShareByBranch].[MarketShare],0) = 0 THEN 0
			ELSE ISNULL([TodayMarketShareByBranch].[MarketShare],0) / [PrevMarketShareByBranch].[MarketShare] - 1
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [TodayMarketShareByBranch]
		ON [BranchTarget].[BranchID] = [TodayMarketShareByBranch].[BranchID]
	LEFT JOIN [PrevMarketShareByBranch]
		ON [BranchTarget].[BranchID] = [PrevMarketShareByBranch].[BranchID]
)

SELECT
	SUM([MarketShare]) [MarketShare]
	, SUM([AbsoluteChange]) [AbsoluteChange]
	, SUM([RelativeChange]) [RelativeChange]
FROM [result]


END

