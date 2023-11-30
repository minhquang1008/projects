/*MTD - BOM - PhaiSinh*/

/*Headline Tag - Market Share (Phần trăm hoàn thành chỉ tiêu tháng - Thị phần) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonthOfCurrentYear DATETIME;
SET @FirstDateOfMonthOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfMonthOfPreviousYear DATETIME;
SET @FirstDateOfMonthOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),MONTH(@DateOfPreviousYear),1,0,0,0,0));

DECLARE @PrevTotalContracts DECIMAL(30,2);
SET @PrevTotalContracts = (
	SELECT
		SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
);

DECLARE @CurrentTotalContracts DECIMAL(30,2);
SET @CurrentTotalContracts = (
	SELECT
		SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
);

WITH 

[TargetByBranch] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [Rel] AS (
	SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] BETWEEN @FirstDateOfMonthOfPreviousYear AND @Date
)

, [PrevMarketShare] AS (
	SELECT
		CAST(CAST(SUM([RRE0018].[SoLuongHopDong]) AS DECIMAL(30,8)) / @PrevTotalContracts / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [RRE0018]
	LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
)

, [CurrentMarketShare] AS (
	SELECT
		CAST(CAST(SUM([RRE0018].[SoLuongHopDong]) AS DECIMAL(30,8)) / @CurrentTotalContracts / 2 AS DECIMAL(30,8)) [MarketShare]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
)

SELECT
	[CurrentMarketShare].[MarketShare] [MarketShare]
	, [CurrentMarketShare].[MarketShare] - [PrevMarketShare].[MarketShare] [AbsoluteChange]
	, CASE 
		WHEN [PrevMarketShare].[MarketShare] = 0 THEN 0
		ELSE [CurrentMarketShare].[MarketShare] / [PrevMarketShare].[MarketShare] - 1
	END [RelativeChange]
FROM [PrevMarketShare]
CROSS JOIN [CurrentMarketShare]


END

