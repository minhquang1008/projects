/*Daily - BOM - PhaiSinh*/

/*Total branches - Market share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @TodayTotalContracts DECIMAL(30,2);
SET @TodayTotalContracts = (
	SELECT
		SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] = @Date
);

WITH

[Branch] AS (
    SELECT DISTINCT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
)

, [TargetByBranch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Fee Income'
        AND [Year] = YEAR(@Date)
)

, [Rel] AS (
    SELECT DISTINCT
        [account_code] [AccountCode]
        , [broker_id] [BrokerID]
        , [branch_id] [BranchID]
    FROM [relationship]
    WHERE [date] = @Date
)

, [ValueTotalBranches] AS (
	SELECT
		[Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[SoLuongHopDong]) / @TodayTotalContracts / 2 [MarketShare]
	FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
    WHERE [RRE0018].[Ngay] = @Date
	GROUP BY [Rel].[BranchID]
)

, [Contribution] AS (
	SELECT
		[BranchID]
		, [MarketShare]
		, CASE [MarketShare] 
			WHEN 0 THEN 0
			ELSE CAST([MarketShare] / SUM([MarketShare]) OVER() AS DECIMAL(7,6))
		END [Contribution]
	FROM [ValueTotalBranches]
)

SELECT
	RANK() OVER(ORDER BY ISNULL([MarketShare], 0) DESC) [Rank]
	, [Branch].[BranchID]
	, ISNULL([MarketShare], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Branch]
LEFT JOIN [Contribution]
	ON [Contribution].[BranchID] = [Branch].[BranchID]
ORDER BY 1


END