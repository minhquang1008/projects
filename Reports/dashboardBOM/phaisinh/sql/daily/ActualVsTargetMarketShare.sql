/*Daily - BOM - PhaiSinh*/

/*Actual vs Target - Market Share*/

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

[TargetByBranch] AS (
    SELECT 
        [BranchID] 
        , CAST(CAST([Target] AS FLOAT) AS DECIMAL(30,8)) [MarketShare]
    FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Market Share'
)

, [Rel] AS (
    SELECT DISTINCT
        [account_code] [AccountCode]
        , [broker_id] [BrokerID]
        , [branch_id] [BranchID]
    FROM [relationship]
    WHERE [date] = @Date
)

, [BranchActual] AS (
    SELECT 
        [Rel].[BranchID] [BranchID]
        , CAST(CAST(SUM([RRE0018].[SoLuongHopDong]) AS DECIMAL(30,8)) / @TodayTotalContracts / 2 AS DECIMAL(30,8)) [MarketShare]
    FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
    WHERE [RRE0018].[Ngay] = @Date
    GROUP BY [Rel].[BranchID]
)

SELECT 
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[MarketShare],0) [Actual]
    , [TargetByBranch].[MarketShare] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END