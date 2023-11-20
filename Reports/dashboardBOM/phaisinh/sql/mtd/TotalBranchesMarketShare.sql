/*MTD - BOM - PhaiSinh*/

/*Total branches - Market share*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @CurrentTotalContracts DECIMAL(30,2);
SET @CurrentTotalContracts = (
	SELECT
		SUM(ISNULL([KhoiLuongKhopLenh],0) + ISNULL([KhoiLuongThoaThuan],0)) [TotalContracts]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichPhaiSinhVietStock]
	WHERE [Ngay] BETWEEN @FirstDateOfMonth AND @Date 
);

WITH

[TargetByBranch] AS (
    SELECT [BranchID]
    FROM [BranchTargetByYear]
    WHERE [Measure] = 'Fee Income'
        AND [Year] = YEAR(@Date)
)

, [Rel] AS (
     SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
    WHERE [date] BETWEEN @FirstDateOfMonth AND @Date
)

, [ValueTotalBranches] AS (
	SELECT 
        [Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[SoLuongHopDong]) / @CurrentTotalContracts / 2 [MarketShare]
    FROM [RRE0018]
   LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
    WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonth AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
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
	[Contribution].[BranchID],
	ISNULL([MarketShare], 0) [Value]
	, ISNULL([Contribution], 0) [Contribution]
FROM [Contribution]
ORDER BY 2 DESC


END