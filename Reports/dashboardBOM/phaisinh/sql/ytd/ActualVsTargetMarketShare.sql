/*YTD - BOM - PhaiSinh*/

/*Actual vs Target - Market Share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @TotalContracts DECIMAL(30,2);
SET @TotalContracts = (
	SELECT
		SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] BETWEEN @FirstDateOfCurrentYear AND @Date 
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
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
    WHERE [date] BETWEEN @FirstDateOfCurrentYear AND @Date
)

, [BranchActual] AS (
    SELECT 
        [Rel].[BranchID] [BranchID]
        , CAST(CAST(SUM([RRE0018].[SoLuongHopDong]) AS DECIMAL(30,8)) / @TotalContracts / 2 AS DECIMAL(30,8)) [MarketShare]
    FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
    WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfCurrentYear AND @Date
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