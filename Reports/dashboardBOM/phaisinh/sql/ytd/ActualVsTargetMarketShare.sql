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
		SUM(ISNULL([KhoiLuongKhopLenh],0) + ISNULL([KhoiLuongThoaThuan],0)) [TotalContracts]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichPhaiSinhVietStock]
	WHERE [Ngay] BETWEEN @FirstDateOfCurrentYear AND @Date 
);

WITH

[TargetByBranch] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] AS DECIMAL(7,6)) [MarketShare]
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
    WHERE [date] BETWEEN @FirstDateOfCurrentYear AND @Date
)

, [BranchActual] AS (
    SELECT 
        [Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[SoLuongHopDong]) / @TotalContracts / 2 [MarketShare]
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


END